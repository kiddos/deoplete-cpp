#include "clang_completer.h"

// excludeDeclarationsFromPCH: allows enumeration of "local" declarations (when
// loading any new translation units)
ClangCompleter::ClangCompleter() : index_(clang_createIndex(1, 1)) {
  parse_option_ = CXTranslationUnit_DetailedPreprocessingRecord |
                  CXTranslationUnit_Incomplete |
                  CXTranslationUnit_PrecompiledPreamble |
                  CXTranslationUnit_CacheCompletionResults |
                  CXTranslationUnit_SkipFunctionBodies |
                  CXTranslationUnit_CreatePreambleOnFirstParse |
                  CXTranslationUnit_KeepGoing;

  complete_option_ = CXCodeComplete_IncludeMacros |
                     CXCodeComplete_IncludeCompletionsWithFixIts;
}

ClangCompleter::~ClangCompleter() {
  for (int i = 0; i < tus_.size(); ++i) {
    clang_disposeTranslationUnit(tus_[i]);
  }
  clang_disposeIndex(index_);
}

void ClangCompleter::Reparse(const std::string& file,
                             const std::string& content) {
  auto it = std::find(files_.begin(), files_.end(), file);
  if (it == files_.end()) {
    AddFile(file, content, CPPArgumentManager());
  } else {
    CXUnsavedFile unsaved_files{
        file.c_str(),
        content.c_str(),
        content.length(),
    };

    int index = std::distance(files_.begin(), it);
    clang_reparseTranslationUnit(tus_[index], 1, &unsaved_files, parse_option_);
  }
}

bool ClangCompleter::HasFile(const std::string& file) {
  return std::find(files_.begin(), files_.end(), file) != files_.end();
}

void ClangCompleter::AddFile(const std::string& file,
                             const ArgumentManager& arg_manager) {
  if (!HasFile(file)) {
    std::vector<char*> args;
    arg_manager.PrepareArgs(args);

    std::ifstream input_file(file);
    if (input_file.is_open()) {
      CXTranslationUnit tu =
          clang_parseTranslationUnit(index_, file.c_str(), &args[0],
                                     args.size(), nullptr, 0, parse_option_);

      tus_.push_back(tu);
      files_.push_back(file);
    }
  }
}

void ClangCompleter::AddFile(const std::string& file,
                             const std::string& content,
                             const ArgumentManager& arg_manager) {
  if (!HasFile(file)) {
    CXUnsavedFile unsaved_files{
        file.c_str(),
        content.c_str(),
        content.length(),
    };

    std::vector<char*> args;
    arg_manager.PrepareArgs(args);

    CXTranslationUnit tu =
        clang_parseTranslationUnit(index_, file.c_str(), &args[0], args.size(),
                                   &unsaved_files, 1, parse_option_);
    tus_.push_back(tu);
    files_.push_back(file);
  }
}

std::string ClangCompleter::GetFileContent(const std::string& file) {
  std::ifstream input_stream(file);
  std::string content((std::istreambuf_iterator<char>(input_stream)),
                      std::istreambuf_iterator<char>());
  return content;
}

std::vector<ClangCompleter::Result> ClangCompleter::CodeComplete(
    const std::string& file, const std::string& content, int line, int column,
    const ArgumentManager& arg_manager) {
  if (!HasFile(file)) {
    AddFile(file, content, arg_manager);
  }

  auto it = std::find(files_.begin(), files_.end(), file);
  int index = std::distance(files_.begin(), it);

  CXTranslationUnit tu = tus_[index];
  CXUnsavedFile unsaved_files{
      file.c_str(),
      content.c_str(),
      content.length(),
  };

  int c = GetCodeCompleteColumn(content, line, column);
  if (last_completion_.file == file &&
      last_completion_.line == line &&
      last_completion_.column == c &&
      last_completion_.result.size() > 0) {
    return last_completion_.result;
  } else {
    CXCodeCompleteResults* results = clang_codeCompleteAt(
        tu, file.c_str(), line, c, &unsaved_files, 1, complete_option_);

    std::vector<Result> outputs;
    if (results) {
      for (int i = 0; i < results->NumResults; ++i) {
        CXCompletionString cs = results->Results[i].CompletionString;
        Result result = GetResult(cs);
        outputs.push_back(result);
      }
    }
    clang_disposeCodeCompleteResults(results);

    last_completion_.file = file;
    last_completion_.line = line;
    last_completion_.column = c;
    last_completion_.result = outputs;
    return outputs;
  }
}

int ClangCompleter::GetCodeCompleteColumn(const std::string& content, int line,
                                          int column) {
  std::string iter_content = content;
  std::vector<std::string> split;
  while (iter_content.size() > 0) {
    int next_line = iter_content.find('\n');
    if (next_line >= 0) {
      std::string l = iter_content.substr(0, next_line);
      iter_content = iter_content.substr(next_line + 1);
      split.push_back(l);
    } else {
      split.push_back(iter_content);
      break;
    }
  }

  if (line <= split.size()) {
    auto search = [](const std::string& s, const std::string& token) -> int {
      return s.rfind(token) + token.size() + 1;
    };
    std::string current_line = split[line - 1].substr(0, column);
    int d1 = search(current_line, "->");
    int d2 = search(current_line, ".");
    int d3 = search(current_line, "::");
    return std::max(std::max(d1, d2), d3);
  }
  return column;
}

ClangCompleter::Result ClangCompleter::GetResult(CXCompletionString cs) {
  Result result;
  int n = clang_getNumCompletionChunks(cs);
  for (int i = 0; i < n; ++i) {
    CXCompletionChunkKind chunk_kind = clang_getCompletionChunkKind(cs, i);

    std::string kind;
    switch (chunk_kind) {
      case CXCompletionChunk_Optional:
        kind = "Optional";
        break;
      case CXCompletionChunk_TypedText:
        kind = "TypedText";
        break;
      case CXCompletionChunk_Text:
        kind = "Text";
        break;
      case CXCompletionChunk_Placeholder:
        kind = "Placeholder";
        break;
      case CXCompletionChunk_Informative:
        kind = "Information";
        break;
      case CXCompletionChunk_CurrentParameter:
        kind = "CurrentParameter";
        break;
      case CXCompletionChunk_LeftParen:
        kind = "LeftParen";
        break;
      case CXCompletionChunk_RightParen:
        kind = "RightParen";
        break;
      case CXCompletionChunk_LeftBracket:
        kind = "LeftBracket";
        break;
      case CXCompletionChunk_RightBracket:
        kind = "RightBracket";
        break;
      case CXCompletionChunk_LeftBrace:
        kind = "LeftBrace";
        break;
      case CXCompletionChunk_RightBrace:
        kind = "RightBrace";
        break;
      case CXCompletionChunk_LeftAngle:
        kind = "LeftAngle";
        break;
      case CXCompletionChunk_RightAngle:
        kind = "RightAngle";
        break;
      case CXCompletionChunk_Comma:
        kind = "Comma";
        break;
      case CXCompletionChunk_ResultType:
        kind = "ResultType";
        break;
      case CXCompletionChunk_Colon:
        kind = "Colon";
        break;
      case CXCompletionChunk_SemiColon:
        kind = "SemiColon";
        break;
      case CXCompletionChunk_Equal:
        kind = "Equal";
        break;
      case CXCompletionChunk_HorizontalSpace:
        kind = "HorizontalSpace";
        break;
      case CXCompletionChunk_VerticalSpace:
        kind = "VerticalSpace";
        break;
    }

    CXString text = clang_getCompletionChunkText(cs, i);
    const char* completion = reinterpret_cast<const char*>(text.data);
    std::string complete_content(completion);

    result.push_back(std::make_pair(kind, complete_content));
  }
  return result;
}
