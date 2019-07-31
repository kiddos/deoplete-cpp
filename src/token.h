#ifndef TOKEN_H
#define TOKEN_H

#include <string>
#include <vector>
#include <iostream>
#include <regex>

bool GetToken(const std::string& content, std::string& token);

std::string FindToken(const std::string& content, int& line, int& col);

#endif /* end of include guard: TOKEN_H */
