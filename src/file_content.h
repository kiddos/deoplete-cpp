#ifndef FILE_CONTENT_H
#define FILE_CONTENT_H

#include <map>
#include <string>
#include <vector>

#include <clang-c/Index.h>

class FileContent : public std::map<std::string, std::string> {
 public:
  FileContent();

  std::vector<CXUnsavedFile> GetUnsavedFiles() const;
  std::vector<CXUnsavedFile> GetUnsavedFiles(
      const std::string& current_file, const std::string& current_file_content);

  void insert(const std::string& file, const std::string& content) {
    (*this)[file] = content;
  }
  bool has_file(const std::string& file) {
    return find(file) != end();
  }
  int file_count() const { return size(); }
};

#endif /* end of include guard: FILE_CONTENT_H */
