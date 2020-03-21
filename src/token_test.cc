#include <string>
#include <sstream>
#include <fstream>

#include <gtest/gtest.h>

#include "token.h"


std::string ReadSource(const std::string& source_path) {
  std::ifstream f(source_path);
  std::stringstream ss;
  if (f.is_open()) {
    ss << f.rdbuf();
  }
  return ss.str();
}

TEST(TestToken, GetToken) {
  std::string token;
  EXPECT_TRUE(GetToken("std::", token));
  EXPECT_EQ(token, "std::");
  EXPECT_TRUE(GetToken("boost::program_options::", token));
  EXPECT_EQ(token, "boost::program_options::");
  EXPECT_TRUE(GetToken("Object::", token));
  EXPECT_EQ(token, "Object::");

  EXPECT_TRUE(GetToken("instance.", token));
  EXPECT_EQ(token, "instance.");
  EXPECT_TRUE(GetToken("instance->", token));
  EXPECT_EQ(token, "instance->");
  EXPECT_TRUE(GetToken("instance.method().", token));
  EXPECT_EQ(token, "instance.method().");
  EXPECT_TRUE(GetToken("instance.method()->", token));
  EXPECT_EQ(token, "instance.method()->");
  EXPECT_TRUE(GetToken("instance.\nmethod().", token));
  EXPECT_EQ(token, "instance.\nmethod().");

  // this is too expensive to compute
  // EXPECT_TRUE(GetToken("instance->\nmethod().", token));
  // EXPECT_EQ(token, "instance->\nmethod().");

  EXPECT_FALSE(GetToken("statement;", token));
  EXPECT_FALSE(GetToken("// comments", token));
  EXPECT_FALSE(GetToken("// comments\n// more comments", token));
  EXPECT_FALSE(GetToken("instance.method()", token));
}

TEST(TestToken, FindToken1) {
  std::string content = ReadSource("./test/sample1.cc");
  int line = 5;
  int column = 8;
  std::string token1 = FindToken(content, line, column);
  EXPECT_EQ(token1, "std::");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 8);

  line = 5;
  column = 2;
  std::string token2 = FindToken(content, line, column);
  EXPECT_EQ(token2, "");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 2);

  line = 5;
  column = 38;
  std::string token3 = FindToken(content, line, column);
  EXPECT_EQ(token3, "std::");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 38);

  line = 5;
  column = 42;
  std::string token4 = FindToken(content, line, column);
  EXPECT_EQ(token4, "std::");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 38);
}

TEST(TestToken, FindToken2) {
  std::string content = ReadSource("./test/sample2.cc");
  int line = 5;
  int column = 10;
  std::string token1 = FindToken(content, line, column);
  EXPECT_EQ(token1, "Eigen::");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 10);

  line = 5;
  column = 2;
  std::string token2 = FindToken(content, line, column);
  EXPECT_EQ(token2, "");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 2);

  line = 2;
  column = 2;
  std::string token3 = FindToken(content, line, column);
  EXPECT_EQ(token3, "");
  EXPECT_EQ(line, 2);
  EXPECT_EQ(column, 2);

  line = 5;
  column = 21;
  std::string token4 = FindToken(content, line, column);
  EXPECT_EQ(token4, "");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 21);

  line = 7;
  column = 2;
  std::string token5 = FindToken(content, line, column);
  EXPECT_EQ(token5, "");
  EXPECT_EQ(line, 7);
  EXPECT_EQ(column, 2);
}

TEST(TestToken, FindToken3) {
  std::string content = ReadSource("./test/sample3.cc");
  int line = 3;
  int column = 11;
  std::string token1 = FindToken(content, line, column);
  EXPECT_EQ(token1, "Abstract::");
  EXPECT_EQ(line, 3);
  EXPECT_EQ(column, 11);

  line = 5;
  column = 17;
  std::string token2 = FindToken(content, line, column);
  EXPECT_EQ(token2, "");
  EXPECT_EQ(line, 5);
  EXPECT_EQ(column, 17);
}

TEST(TestToken, FindToken4) {
  std::string content = ReadSource("./test/sample4.cc");
  int line = 10;
  int column = 16;
  std::string token1 = FindToken(content, line, column);
  EXPECT_EQ(token1, "");
  EXPECT_EQ(line, 10);
  EXPECT_EQ(column, 16);

  line = 12;
  column = 20;
  std::string token2 = FindToken(content, line, column);
  EXPECT_EQ(token2, "t2->");
  EXPECT_EQ(line, 12);
  EXPECT_EQ(column, 20);

  line = 12;
  column = 21;
  std::string token3 = FindToken(content, line, column);
  EXPECT_EQ(token3, "t2->");
  EXPECT_EQ(line, 12);
  EXPECT_EQ(column, 20);

  line = 12;
  column = 27;
  std::string token4 = FindToken(content, line, column);
  EXPECT_EQ(token4, "t.");
  EXPECT_EQ(line, 12);
  EXPECT_EQ(column, 27);

  line = 12;
  column = 28;
  std::string token5 = FindToken(content, line, column);
  EXPECT_EQ(token5, "t.");
  EXPECT_EQ(line, 12);
  EXPECT_EQ(column, 27);
}

TEST(TestToken, FindToken5) {
  std::string content = ReadSource("./test/sample5.cc");
  int line = 21;
  int column = 6;
  std::string token1 = FindToken(content, line, column);
  EXPECT_EQ(token1, "A::");
  EXPECT_EQ(line, 21);
  EXPECT_EQ(column, 6);

  line = 21;
  column = 7;
  std::string token2 = FindToken(content, line, column);
  EXPECT_EQ(token2, "A::");
  EXPECT_EQ(line, 21);
  EXPECT_EQ(column, 6);

  line = 21;
  column = 16;
  std::string token3 = FindToken(content, line, column);
  EXPECT_EQ(token3, "A::B::");
  EXPECT_EQ(line, 21);
  EXPECT_EQ(column, 9);

  line = 21;
  column = 9;
  std::string token4 = FindToken(content, line, column);
  EXPECT_EQ(token4, "A::B::");
  EXPECT_EQ(line, 21);
  EXPECT_EQ(column, 9);

  line = 22;
  column = 4;
  std::string token5 = FindToken(content, line, column);
  EXPECT_EQ(token5, "");
  EXPECT_EQ(line, 22);
  EXPECT_EQ(column, 4);

  line = 22;
  column = 5;
  std::string token6 = FindToken(content, line, column);
  EXPECT_EQ(token6, "c.");
  EXPECT_EQ(line, 22);
  EXPECT_EQ(column, 5);

  line = 22;
  column = 10;
  std::string token7 = FindToken(content, line, column);
  EXPECT_EQ(token7, "c.");
  EXPECT_EQ(line, 22);
  EXPECT_EQ(column, 5);

  line = 23;
  column = 11;
  std::string token8 = FindToken(content, line, column);
  EXPECT_EQ(token8, "c.bar().");
  EXPECT_EQ(line, 23);
  EXPECT_EQ(column, 11);
}

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
