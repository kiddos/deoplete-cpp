#include <chrono>

#include <gtest/gtest.h>

#include "c_argument_manager.h"
#include "clang_completer.h"
#include "cpp_argument_manager.h"
#include "objc_argument_manager.h"
#include "objcpp_argument_manager.h"

class TestClangCompleter : public ::testing::Test {
 public:
  TestClangCompleter() {
    cpp_arg_manager_.AddIncludePath("/usr/local/include");
    cpp_arg_manager_.AddIncludePath("/usr/include/eigen3");

    objc_arg_manager_.AddIncludePath("/usr/include/GNUstep");
    objcpp_arg_manager_.AddIncludePath("/usr/include/GNUstep");
  }

  void SetUp() override { start_ = std::chrono::system_clock::now(); }

  void TearDown() override {
    end_ = std::chrono::system_clock::now();
    auto passed = end_ - start_;
    std::cout
        << "time passed: "
        << std::chrono::duration_cast<std::chrono::milliseconds>(passed).count()
        << std::endl;
  }

  bool ContainResult(const std::vector<ClangCompleter::Result>& results,
                     const std::string& text) {
    for (int i = 0; i < results.size(); ++i) {
      ClangCompleter::Result result = results[i];
      for (int j = 0; j < result.size(); ++j) {
        if (result[j].first == "TypedText" && result[j].second == text) {
          return true;
        }
      }
    }
    return false;
  }

 protected:
  std::chrono::system_clock::time_point start_, end_;

  ClangCompleter engine_;
  CArgumentManager c_arg_manager_;
  CPPArgumentManager cpp_arg_manager_;
  OBJCArgumentManager objc_arg_manager_;
  OBJCPPArgumentManager objcpp_arg_manager_;

  void EchoResults(const std::vector<ClangCompleter::Result>& results) {
    for (int i = 0; i < results.size(); ++i) {
      for (int j = 0; j < results[i].size(); ++j) {
        std::cout << results[i][j].first << ": " << results[i][j].second
                  << ", ";
      }
      std::cout << std::endl;
    }
  }
};

TEST_F(TestClangCompleter, TestCStdIOLibrary) {
  std::string file = "./test/sample1.c";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 5, 1, c_arg_manager_);

  // test common function exists
  EXPECT_TRUE(ContainResult(results, "printf"));
  EXPECT_TRUE(ContainResult(results, "vprintf"));
  EXPECT_TRUE(ContainResult(results, "scanf"));

  EXPECT_TRUE(ContainResult(results, "fprintf"));
  EXPECT_TRUE(ContainResult(results, "fscanf"));
  EXPECT_TRUE(ContainResult(results, "fopen"));
  EXPECT_TRUE(ContainResult(results, "fclose"));
  EXPECT_TRUE(ContainResult(results, "fread"));
  EXPECT_TRUE(ContainResult(results, "fwrite"));
  EXPECT_TRUE(ContainResult(results, "fseek"));
  EXPECT_TRUE(ContainResult(results, "clearerr"));
  EXPECT_TRUE(ContainResult(results, "feof"));
  EXPECT_TRUE(ContainResult(results, "fflush"));
  EXPECT_TRUE(ContainResult(results, "fgetpos"));

  // test macro exists
  EXPECT_TRUE(ContainResult(results, "NULL"));
  EXPECT_TRUE(ContainResult(results, "EOF"));
  EXPECT_TRUE(ContainResult(results, "stdout"));
  EXPECT_TRUE(ContainResult(results, "stdin"));
  EXPECT_TRUE(ContainResult(results, "stderr"));
}

TEST_F(TestClangCompleter, TestCCustomDataStructure) {
  std::string file = "./test/sample2.c";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 24, 5, c_arg_manager_);

  EXPECT_TRUE(ContainResult(results, "i"));
  EXPECT_TRUE(ContainResult(results, "d"));

  std::vector<ClangCompleter::Result> results2 =
      engine_.CodeComplete(file, content, 25, 8, c_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "i"));
  EXPECT_TRUE(ContainResult(results, "d"));
}

TEST_F(TestClangCompleter, TestDefaultNamespace) {
  std::string file = "./test/sample1.cc";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 4, 1, cpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "std"));
}

TEST_F(TestClangCompleter, TestIncludeComplexLibrary) {
  std::string file = "./test/sample2.cc";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 5, 10, cpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "Matrix4f"));

  // test for time
  engine_.CodeComplete(file, content, 7, 8, cpp_arg_manager_);
}

TEST_F(TestClangCompleter, TestIncludeLibrary) {
  std::string file = "./test/sample3.cc";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 3, 11, cpp_arg_manager_);

  EXPECT_TRUE(ContainResult(results, "Abstract"));
  EXPECT_TRUE(ContainResult(results, "Foo"));
  EXPECT_TRUE(ContainResult(results, "Bar"));
}

TEST_F(TestClangCompleter, TestCompleteUnsavedFile) {
  std::string file = "./test/unsaved_file.cc";
  std::string content =
      "#include <iostream>\n"
      "int main() {\n"
      "  std::\n"
      "}\n";

  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 3, 8, cpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "cout"));
}

TEST_F(TestClangCompleter, TestReparse) {
  std::string file = "./test/sample1.cc";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 4, 1, cpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "std"));

  engine_.Reparse(file, content);
  std::vector<ClangCompleter::Result> results2 =
      engine_.CodeComplete(file, content, 4, 1, cpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results2, "std"));
}

TEST_F(TestClangCompleter, TestReparseUnsavdFile) {
  std::string file = "./test/unsaved_file.cc";
  std::string content =
      "#include <iostream>\n"
      "int main() {\n"
      "  std::\n"
      "}\n";

  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 3, 8, cpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "cout"));

  engine_.Reparse(file, content);
  std::vector<ClangCompleter::Result> results2 =
      engine_.CodeComplete(file, content, 3, 8, cpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "cout"));
}

TEST_F(TestClangCompleter, TestAddFileSuccess) {
  std::string file = "./test/sample1.cc";
  engine_.AddFile(file, cpp_arg_manager_);
  EXPECT_EQ(engine_.file_count(), 1);
}

TEST_F(TestClangCompleter, TestAddUnsavedFileWithContent) {
  std::string file = "./test/unsaved_file.cc";
  std::string content =
      "#include <iostream>\n"
      "int main() {\n"
      "  std::\n"
      "}\n";

  engine_.AddFile(file, content, cpp_arg_manager_);
  EXPECT_EQ(engine_.file_count(), 1);
}

TEST_F(TestClangCompleter, TestCannotAddUnsavedFileWithoutContent) {
  std::string file = "./test/unsaved_file.cc";
  engine_.AddFile(file, cpp_arg_manager_);
  EXPECT_EQ(engine_.file_count(), 0);
}

TEST_F(TestClangCompleter, TestCodeCompletePosition) {
  std::string file = "./test/sample4.cc";
  std::string content = engine_.GetFileContent(file);
  int c = engine_.GetCodeCompleteColumn(content, 12, 8);
  EXPECT_EQ(c, 8);

  c = engine_.GetCodeCompleteColumn(content, 12, 10);
  EXPECT_EQ(c, 8);

  c = engine_.GetCodeCompleteColumn(content, 12, 12);
  EXPECT_EQ(c, 8);

  c = engine_.GetCodeCompleteColumn(content, 12, 20);
  EXPECT_EQ(c, 20);

  c = engine_.GetCodeCompleteColumn(content, 12, 22);
  EXPECT_EQ(c, 20);

  c = engine_.GetCodeCompleteColumn(content, 12, 24);
  EXPECT_EQ(c, 20);

  c = engine_.GetCodeCompleteColumn(content, 12, 27);
  EXPECT_EQ(c, 27);

  c = engine_.GetCodeCompleteColumn(content, 12, 29);
  EXPECT_EQ(c, 27);

  c = engine_.GetCodeCompleteColumn(content, 12, 31);
  EXPECT_EQ(c, 27);

  c = engine_.GetCodeCompleteColumn(content, 12, 37);
  EXPECT_EQ(c, 37);

  c = engine_.GetCodeCompleteColumn(content, 12, 39);
  EXPECT_EQ(c, 37);
}

TEST_F(TestClangCompleter, TestObjcBasicLibrary) {
  std::string file = "./test/sample1.m";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 6, 1, objc_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "@\""));
  EXPECT_TRUE(ContainResult(results, "@{"));
}

TEST_F(TestClangCompleter, TestObjcppBasicLibrary) {
  std::string file = "./test/sample1.m";
  std::string content = engine_.GetFileContent(file);
  std::vector<ClangCompleter::Result> results =
      engine_.CodeComplete(file, content, 6, 1, objcpp_arg_manager_);
  EXPECT_TRUE(ContainResult(results, "@\""));
  EXPECT_TRUE(ContainResult(results, "@{"));
}

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
