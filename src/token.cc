#include "token.h"

bool GetToken(const std::string& content, std::string& token) {
  std::regex pattern("([^=+\\-*/\\^\\&;{}<>:\\.\"']+(::|->|\\.)$)");
  std::smatch match;
  bool result = std::regex_search(content, match, pattern);
  if (match.size() > 0) {
    token = match[0];
  }

  // for (auto m : match) {
  //   std::cout << "match: " << m << std::endl;
  // }
  // std::cout << std::endl;
  return result;
}

int LocateIndex(const std::string& content, int line, int column) {
  std::string it = content;
  int line_count = 1;
  int index = 0;
  while (it.length() > 0 && line_count < line) {
    int found = it.find("\n");
    if (found != std::string::npos) {
      it = it.substr(found + 1);
      index += found + 1;
      ++line_count;
    } else {
      break;
    }
  }
  index += column;
  return index - 1;
}

std::string StripToken(const std::string& token) {
  std::string result;
  std::vector<char> space_chars = {' ', '\t', '\r', '\b', '\n'};
  for (int i = 0; i < token.length(); ++i) {
    bool found = false;
    for (int j = 0; j < space_chars.size(); ++j) {
      if (token[i] == space_chars[j]) {
        found = true;
      }
    }
    if (!found) {
      result += token[i];
    }
  }
  return result;
}

int FindLastOccurrence(const std::string& content,
                       const std::vector<std::string>& delimiters) {
  int best = -1;
  for (int i = 0; i < delimiters.size(); ++i) {
    int found = content.find_last_of(delimiters[i]);
    if (found != std::string::npos && found > best) {
      // std::cout << "found: " << delimiters[i] << ", at: " << found <<
      // std::endl;
      best = found;
    }
  }
  return best;
}

void ComputeLocation(const std::string& content, int found, int& line,
                     int& column) {
  std::string it = content;
  int index = 0;
  line = 1;
  while (it.length() > 0) {
    int nl = it.find("\n");
    if (nl != std::string::npos) {
      it = it.substr(nl + 1);
      if (index + nl + 1 > found) {
        break;
      }
      index += nl + 1;
      ++line;
      // std::cout << "index: " << index << ", found: " << found << std::endl;
    } else {
      break;
    }
  }
  column = found - index + 2;
}

std::string FindToken(const std::string& content, int& line, int& column) {
  int index = LocateIndex(content, line, column);
  std::string part = content.substr(0, index);
  // std::cout << "part: " << part << std::endl;

  std::vector<std::string> delimiters = {"::", "->", ".", "}", "{",
                                         "=",  "+",  "-", "*", "/",
                                         "&",  "^",  "<", ">", ";"};
  int last_delimiter = FindLastOccurrence(part, delimiters);
  if (last_delimiter != std::string::npos) {
    part = part.substr(0, last_delimiter + 1);
    // std::cout << "stripped part: " << part << std::endl;
    std::string token;
    if (GetToken(part, token)) {
      ComputeLocation(content, last_delimiter, line, column);
      return StripToken(token);
    }
  }
  return "";
}
