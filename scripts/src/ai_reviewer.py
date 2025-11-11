# scripts/src/ai_reviewer.py
"""
AI 리뷰 생성 모듈 (Phase 7)
OpenAI GPT-4 API를 사용하여 강의 리뷰 자동 생성
"""

import json
from typing import Dict, List, Optional
from openai import OpenAI
from src.logger_config import logger
from src.config import config


class AIReviewer:
    """OpenAI GPT-4 기반 강의 리뷰 생성기"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        prompt_version: str = "1.0.0"
    ):
        """
        AIReviewer 초기화

        Args:
            api_key: OpenAI API 키 (None이면 config에서 로드)
            model: 사용할 GPT 모델 (None이면 config에서 로드)
            prompt_version: 프롬프트 버전 (기본값: 1.0.0)
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        self.model = model or config.OPENAI_MODEL
        self.prompt_version = prompt_version
        self.max_tokens = config.MAX_TOKENS
        self.temperature = config.TEMPERATURE

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다.\n"
                "  .env 파일에 OPENAI_API_KEY를 설정하거나\n"
                "  AIReviewer(api_key='sk-...') 형태로 직접 전달하세요."
            )

        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"AIReviewer 초기화 완료: model={self.model}, version={self.prompt_version}")

    def generate_review(self, course_data: Dict) -> Dict:
        """
        강의 정보를 기반으로 AI 리뷰 생성

        Args:
            course_data: 강의 정보 딕셔너리
                - title: 강의 제목
                - instructor: 강사명
                - original_price: 정가
                - sale_price: 할인가
                - discount_rate: 할인율
                - rating: 평점
                - review_count: 리뷰 수
                - student_count: 수강생 수

        Returns:
            dict: {
                "review_text": str,
                "rating": float,
                "key_strengths": List[str],
                "recommended_for": List[str],
                "tokens_used": int,
                "model_version": str,
                "prompt_version": str
            }

        Raises:
            ValueError: 응답 형식이 올바르지 않은 경우
            Exception: API 호출 실패 시
        """
        try:
            # 1. 프롬프트 생성
            prompt = self._build_prompt(course_data)

            # 2. OpenAI API 호출
            logger.info(f"리뷰 생성 중: {course_data.get('title', 'Unknown')}")
            logger.debug(f"Model: {self.model}, Tokens: {self.max_tokens}, Temp: {self.temperature}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )

            # 3. 응답 파싱
            content = response.choices[0].message.content
            review_data = json.loads(content)

            # 4. 응답 검증
            if not self._validate_response(review_data):
                raise ValueError(f"유효하지 않은 응답 형식: {review_data}")

            # 5. 메타데이터 추가
            result = {
                "review_text": review_data["review"],
                "rating": float(review_data["rating"]),
                "key_strengths": review_data.get("key_strengths", []),
                "recommended_for": review_data.get("recommended_for", []),
                "tokens_used": response.usage.total_tokens,
                "model_version": self.model,
                "prompt_version": self.prompt_version
            }

            logger.info(
                f"✅ 리뷰 생성 성공: {len(result['review_text'])}자, "
                f"토큰: {result['tokens_used']}"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            logger.debug(f"응답 내용: {content if 'content' in locals() else 'N/A'}")
            raise

        except Exception as e:
            logger.error(f"리뷰 생성 실패: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 반환"""
        return """당신은 IT 교육 전문가이자 온라인 강의 리뷰어입니다.
강의 정보를 분석하여 공정하고 신뢰할 수 있는 리뷰를 작성합니다.
자연스러운 한국어로 작성하며, 과장된 표현은 피합니다."""

    def _build_prompt(self, course_data: Dict) -> str:
        """강의 정보를 기반으로 프롬프트 생성"""
        title = course_data.get("title", "제목 없음")
        instructor = course_data.get("instructor", "강사 정보 없음")
        original_price = course_data.get("original_price", 0)
        sale_price = course_data.get("sale_price", original_price)
        discount_rate = course_data.get("discount_rate", 0)
        rating = course_data.get("rating", 0.0)
        review_count = course_data.get("review_count", 0)
        student_count = course_data.get("student_count", 0)

        return f"""다음 인프런 강의에 대한 리뷰를 작성해주세요.

강의 정보:
- 제목: {title}
- 강사: {instructor}
- 가격: {original_price:,}원 → {sale_price:,}원 (할인율: {discount_rate}%)
- 현재 평점: {rating}/5.0 (리뷰 {review_count}개)
- 수강생: {student_count:,}명

작성 지침:
1. 200-300자 분량의 리뷰를 작성하세요
2. 강의의 장점과 추천 대상을 구체적으로 언급하세요
3. 가격 대비 가치를 평가하세요
4. 자연스럽고 신뢰할 수 있는 톤을 유지하세요
5. "강력 추천", "최고의 강의" 같은 과장된 표현은 피하세요

출력 형식 (JSON):
{{
  "review": "리뷰 텍스트 (200-300자)",
  "rating": 4.5,
  "key_strengths": ["장점1", "장점2", "장점3"],
  "recommended_for": ["대상1", "대상2"]
}}"""

    def _validate_response(self, response: Dict) -> bool:
        """생성된 리뷰 응답 검증"""
        required_fields = ["review", "rating", "key_strengths", "recommended_for"]

        # 1. 필수 필드 확인
        if not all(field in response for field in required_fields):
            missing = [f for f in required_fields if f not in response]
            logger.warning(f"필수 필드 누락: {missing}")
            return False

        # 2. 리뷰 길이 확인 (200-500자)
        review_length = len(response["review"])
        if not (150 <= review_length <= 600):
            logger.warning(
                f"리뷰 길이 범위 벗어남: {review_length}자 "
                f"(권장: 200-300자, 허용: 150-600자)"
            )
            # 경고만 하고 통과 (약간의 유연성 허용)

        # 3. 평점 범위 확인 (0-5.0)
        try:
            rating = float(response["rating"])
            if not (0 <= rating <= 5.0):
                logger.warning(f"평점 범위 오류: {rating} (0-5.0 범위 필요)")
                return False
        except (ValueError, TypeError) as e:
            logger.warning(f"평점 타입 오류: {response['rating']} - {e}")
            return False

        # 4. 배열 타입 확인
        if not isinstance(response["key_strengths"], list):
            logger.warning(f"key_strengths가 배열이 아님: {type(response['key_strengths'])}")
            return False

        if not isinstance(response["recommended_for"], list):
            logger.warning(f"recommended_for가 배열이 아님: {type(response['recommended_for'])}")
            return False

        # 5. 배열 내용 확인 (비어있지 않아야 함)
        if len(response["key_strengths"]) == 0:
            logger.warning("key_strengths 배열이 비어있음")
            # 경고만 하고 통과

        if len(response["recommended_for"]) == 0:
            logger.warning("recommended_for 배열이 비어있음")
            # 경고만 하고 통과

        return True


# 테스트용 메인 함수
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("AIReviewer 테스트 시작")
    logger.info("=" * 60)

    # 샘플 강의 데이터
    sample_course = {
        "title": "[왕초보편] 앱 8개를 만들면서 배우는 안드로이드 코틀린",
        "instructor": "개복치개발자",
        "original_price": 24200,
        "sale_price": 24200,
        "discount_rate": 0,
        "rating": 4.8,
        "review_count": 216,
        "student_count": 3420
    }

    try:
        # AIReviewer 초기화
        reviewer = AIReviewer()

        # 리뷰 생성
        logger.info("\n샘플 강의로 리뷰 생성 테스트...")
        review = reviewer.generate_review(sample_course)

        # 결과 출력
        logger.info("\n" + "=" * 60)
        logger.info("생성된 리뷰:")
        logger.info("=" * 60)
        logger.info(f"\n{review['review_text']}\n")
        logger.info(f"평점: {review['rating']}/5.0")
        logger.info(f"주요 장점: {', '.join(review['key_strengths'])}")
        logger.info(f"추천 대상: {', '.join(review['recommended_for'])}")
        logger.info(f"\n토큰 사용량: {review['tokens_used']}")
        logger.info(f"모델: {review['model_version']}")
        logger.info(f"프롬프트 버전: {review['prompt_version']}")
        logger.info("=" * 60)
        logger.info("✅ 테스트 완료!")

    except ValueError as e:
        logger.error(f"❌ 설정 오류: {e}")
        logger.info("\n.env 파일에 OPENAI_API_KEY를 설정하세요:")
        logger.info("  OPENAI_API_KEY=sk-proj-your_key_here")

    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
        import traceback
        logger.debug(traceback.format_exc())
