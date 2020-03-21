#ifndef FILE_CONTENT_H
#define FILE_CONTENT_H

#include <map>
#include <string>
#include <vector>

#include <clang-c/Index.h>

#include "argument_manager.h"

class FileContent {
 public:
  FileContent();

  std::vector<CXUnsavedFile> GetUnsavedFiles() const;
  std::vector<CXUnsavedFile> GetUnsavedFiles(
      const std::string& current_file, const std::string& current_file_content);

  void insert(const std::string& file, const std::string& content) {
    content_[file] = content;
  }
  bool has_file(const std::string& file) {
    return content_.find(file) != content_.end();
  }
  std::map<std::string, std::string> content() const { return content_; }
  int file_count() const { return content_.size(); }

 private:
  std::map<std::string, std::string> content_;
};

#endif /* end of include guard: FILE_CONTENT_H */
