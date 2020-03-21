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
  for (auto it = files_.begin(); it != files_.end(); ++it) {
    FileContent content = it->second;
    clang_disposeTranslationUnit(content.second);
  }
  clang_disposeIndex(index_);
}

void ClangCompleter::Parse(const std::string& file, const std::string& content,
                           const ArgumentManager& arg_manager) {
  std::vector<CXUnsavedFile> unsaved_files;
  unsaved_files.push_back(CXUnsavedFile{
      file.c_str(),
      content.c_str(),
      content.length(),
  });
  for (auto it = files_.begin(); it != files_.end(); ++it) {
    if (it->first != file) {
      unsaved_files.push_back(CXUnsavedFile{
          it->first.c_str(),
          it->second.first.c_str(),
          it->second.first.length(),
      });
    }
  }

  if (files_.find(file) != files_.end()) {
    // already added
    CXTranslationUnit tu = files_[file].second;
    clang_reparseTranslationUnit(tu, unsaved_files.size(), &unsaved_files[0],
                                 clang_defaultReparseOptions(tu));

    cache_.clear();
    std::string c = content;
    files_[file] = std::make_pair(c, tu);
  } else {
    // add translation unit
    std::vector<char*> args;
    arg_manager.PrepareArgs(args);

    CXTranslationUnit tu =
        clang_parseTranslationUnit(index_, file.c_str(), &args[0], args.size(),
                                   &unsaved_files[0], unsaved_files.size(), parse_option_);
    std::string c = content;
    files_[file] = std::make_pair(c, tu);
  }
}

void ClangCompleter::Update(const ArgumentManager& arg_manager) {
  for (auto it = cache_.begin(); it != cache_.end(); ++it) {
    CacheData data = it->second;
    CompletionLocation loc = data.first;
    if (loc.snap_shot.length() > 0) {
      std::vector<Result> new_results = ObtainCodeCompleteResult(
          loc.file, loc.snap_shot, loc.line, loc.column, arg_manager);
      if (new_results.size() > data.second.size()) {
        loc.snap_shot = "";
        it->second = std::make_pair(loc, new_results);
      }
    }
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
  std::vector<CXUnsavedFile> unsaved_files;
  unsaved_files.push_back(CXUnsavedFile{
      file.c_str(),
      content.c_str(),
      content.length(),
  });
  for (auto it = files_.begin(); it != files_.end(); ++it) {
    if (it->first != file) {
      unsaved_files.push_back(CXUnsavedFile{
          it->first.c_str(),
          it->second.first.c_str(),
          it->second.first.length(),
      });
    }
  }

  CXCodeCompleteResults* results = clang_codeCompleteAt(
      tu, file.c_str(), line, column, &unsaved_files[0], unsaved_files.size(), complete_option_);

  std::vector<Result> outputs;
  if (results) {
    clang_sortCodeCompletionResults(results->Results, results->NumResults);

    for (int i = 0; i < results->NumResults; ++i) {
      CXCompletionString cs = results->Results[i].CompletionString;
      Result result = GetResult(cs);
      outputs.push_back(result);
    }
    clang_disposeCodeCompleteResults(results);
  }

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
    cache_[token].first.snap_shot = content;
    cache_[token].first.line = l;
    cache_[token].first.column = c;
    return data.second;
  } else {
    std::vector<Result> outputs =
        ObtainCodeCompleteResult(file, content, l, c, arg_manager);
    CompletionLocation loc = {file, content, l, c};
    if (ShouldCache(token)) {
      CacheData data = std::make_pair(loc, outputs);
      cache_[token] = data;
    }
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

bool ClangCompleter::ShouldCache(const std::string& token) {
  return token.length() > 2 && token.substr(token.length() - 2) == "::";
}
