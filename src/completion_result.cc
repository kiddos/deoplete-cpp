#include "completion_result.h"

CompletionResult ParseResult(CXCompletionString cs) {
  CompletionResult result;
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
