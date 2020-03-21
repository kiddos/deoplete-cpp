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
  for (auto it = trans_units_.begin(); it != trans_units_.end(); ++it) {
    clang_disposeTranslationUnit(it->second);
  }
  clang_disposeIndex(index_);
}

void ClangCompleter::Parse(const std::string& file, const std::string& content,
                           const ArgumentManager& arg_manager) {
  std::vector<CXUnsavedFile> unsaved_files =
      content_.GetUnsavedFiles(file, content);

  if (trans_units_.find(file) != trans_units_.end()) {
    // already added
    CXTranslationUnit trans_unit = trans_units_[file];
    clang_reparseTranslationUnit(trans_unit, unsaved_files.size(),
                                 &unsaved_files[0],
                                 clang_defaultReparseOptions(trans_unit));

    cache_.clear();
    trans_units_[file] = trans_unit;
  } else {
    // add translation unit
    std::vector<char*> args;
    arg_manager.PrepareArgs(args);

    CXTranslationUnit tu = clang_parseTranslationUnit(
        index_, file.c_str(), &args[0], args.size(), &unsaved_files[0],
        unsaved_files.size(), parse_option_);
    trans_units_[file] = tu;
  }
}

void ClangCompleter::Update() {
  std::vector<CXUnsavedFile> unsaved_files = content_.GetUnsavedFiles();
  for (auto it = trans_units_.begin(); it != trans_units_.end(); ++it) {
    clang_reparseTranslationUnit(it->second, unsaved_files.size(),
                                 &unsaved_files[0],
                                 clang_defaultReparseOptions(it->second));
  }

  cache_.clear();
}

std::vector<ClangCompleter::Result> ClangCompleter::ObtainCodeCompleteResult(
    const std::string& file, const std::string& content, int line, int column,
    const ArgumentManager& arg_manager) {
  Parse(file, content, arg_manager);

  CXTranslationUnit trans_unit = trans_units_[file];
  std::vector<CXUnsavedFile> unsaved_files =
      content_.GetUnsavedFiles(file, content);
  CXCodeCompleteResults* results = clang_codeCompleteAt(
      trans_unit, file.c_str(), line, column, &unsaved_files[0],
      unsaved_files.size(), complete_option_);

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
    // if (ShouldCache(token)) {
    CacheData data = std::make_pair(loc, outputs);
    cache_[token] = data;
    // }
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
      default:
        kind = "unknown";
        break;
    }

    CXString text = clang_getCompletionChunkText(cs, i);
    const char* completion = reinterpret_cast<const char*>(text.data);
    std::string complete_content(completion);

    result.push_back(std::make_pair(kind, complete_content));
  }
  return result;
}
