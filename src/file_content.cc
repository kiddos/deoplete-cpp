#include "file_content.h"

FileContent::FileContent() {}

std::vector<CXUnsavedFile> FileContent::GetUnsavedFiles() const {
  std::vector<CXUnsavedFile> unsaved_files;

  for (auto it = begin(); it != end(); ++it) {
    unsaved_files.push_back(CXUnsavedFile{
        it->first.c_str(),
        it->second.c_str(),
        it->second.length(),
    });
  }
  return unsaved_files;
}

std::vector<CXUnsavedFile> FileContent::GetUnsavedFiles(
    const std::string& file, const std::string& content) {
  insert(file, content);

  std::vector<CXUnsavedFile> unsaved_files;
  for (auto it = begin(); it != end(); ++it) {
    unsaved_files.push_back(CXUnsavedFile{
        it->first.c_str(),
        it->second.c_str(),
        it->second.length(),
    });
  }
  return unsaved_files;
}
