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

CompletionResults ClangCompleter::ObtainCodeCompleteResult(
    const std::string& file, const std::string& content, int line, int column,
    const ArgumentManager& arg_manager) {
  Parse(file, content, arg_manager);

  CXTranslationUnit trans_unit = trans_units_[file];
  std::vector<CXUnsavedFile> unsaved_files =
      content_.GetUnsavedFiles(file, content);
  CXCodeCompleteResults* results = clang_codeCompleteAt(
      trans_unit, file.c_str(), line, column, &unsaved_files[0],
      unsaved_files.size(), complete_option_);

  std::vector<CompletionResult> outputs;
  if (results) {
    clang_sortCodeCompletionResults(results->Results, results->NumResults);

    for (int i = 0; i < results->NumResults; ++i) {
      CXCompletionString cs = results->Results[i].CompletionString;
      CompletionResult result = ParseResult(cs);
      outputs.push_back(result);
    }
    clang_disposeCodeCompleteResults(results);
  }

  return outputs;
}

CompletionResults ClangCompleter::CodeComplete(
    const std::string& file, const std::string& content, int line, int column,
    const ArgumentManager& arg_manager) {
  std::string token = FindToken(content, line, column);
  if (cache_.has_cache(token)) {
    return cache_[token];
  } else {
    std::vector<CompletionResult> results =
        ObtainCodeCompleteResult(file, content, line, column, arg_manager);
    cache_[token] = results;
    return results;
  }
}
