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

  complete_option_ = CXCodeComplete_IncludeMacros;
}

ClangCompleter::~ClangCompleter() {
  for (auto it = files_.begin(); it != files_.end(); ++it) {
    FileContent content = it->second;
    clang_disposeTranslationUnit(content.second);
  }
  clang_disposeIndex(index_);
}

void ClangCompleter::Parse(const std::string& file, const std::string& content,
                           const ArgumentManager& arg_manager) {
  if (files_.find(file) != files_.end()) {
    // already added
    CXUnsavedFile unsaved_files{
        file.c_str(),
        content.c_str(),
        content.length(),
    };
    clang_reparseTranslationUnit(files_[file].second, 1, &unsaved_files,
                                 parse_option_);
  } else {
    // add translation unit
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
    std::string c = content;
    files_[file] = std::make_pair(c, tu);
  }
}

void ClangCompleter::Update(const ArgumentManager& arg_manager) {
  for (auto it = cache_.begin(); it != cache_.end(); ++it) {
    CacheData data = it->second;
    CompletionLocation loc = data.first;
    std::vector<Result> new_results = ObtainCodeCompleteResult(
        loc.file, files_[loc.file].first, loc.line, loc.column, arg_manager);
    it->second = std::make_pair(loc, new_results);
  }
}

std::string ClangCompleter::GetFileContent(const std::string& file) {
  std::ifstream input_stream(file);
  std::string content((std::istreambuf_iterator<char>(input_stream)),
                      std::istreambuf_iterator<char>());
  return content;
}

std::vector<ClangCompleter::Result> ClangCompleter::ObtainCodeCompleteResult(
    const std::string& file, const std::string& content, int line, int column,
    const ArgumentManager& arg_manager) {
  Parse(file, content, arg_manager);

  CXTranslationUnit tu = files_[file].second;
  CXUnsavedFile unsaved_files{
      file.c_str(),
      content.c_str(),
      content.length(),
  };

  CXCodeCompleteResults* results = clang_codeCompleteAt(
      tu, file.c_str(), line, column, &unsaved_files, 1, complete_option_);

  std::vector<Result> outputs;
  if (results) {
    for (int i = 0; i < results->NumResults; ++i) {
      CXCompletionString cs = results->Results[i].CompletionString;
      Result result = GetResult(cs);
      outputs.push_back(result);
    }
  }
  clang_disposeCodeCompleteResults(results);
  return outputs;
}

std::vector<ClangCompleter::Result> ClangCompleter::CodeComplete(
    const std::string& file, const std::string& content, int line, int column,
    const ArgumentManager& arg_manager) {
  int l = line;
  int c = column;
  std::string token = FindToken(content, l, c);
  if (cache_.find(token) != cache_.end()) {
    CacheData data = cache_[token];
    cache_[token].first.line = l;
    cache_[token].first.column = c;
    return data.second;
  } else {
    std::vector<Result> outputs =
        ObtainCodeCompleteResult(file, content, l, c, arg_manager);
    CompletionLocation loc = {file, l, c};
    CacheData data = std::make_pair(loc, outputs);
    cache_[token] = data;
    return outputs;
  }
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
