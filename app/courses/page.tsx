// app/courses/page.tsx
import { supabase } from "@/lib/supabase";

export const revalidate = 3600; // 1시간마다 재생성 (ISR)

export default async function CoursesPage() {
  // Supabase에서 강의 데이터 가져오기
  const { data: courses, error } = await supabase
    .from("courses")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    return (
      <div className="container mx-auto px-4 py-16">
        <p className="text-red-600">데이터 로드 실패: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold mb-8">전체 강의 목록</h1>

      {courses && courses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div
              key={course.id}
              className="border rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <h2 className="text-xl font-semibold mb-2">{course.title}</h2>
              <p className="text-gray-600 mb-2">강사: {course.instructor}</p>
              <div className="flex items-center justify-between">
                <span className="text-primary-600 font-bold">
                  {course.discount_price_krw
                    ? `₩${course.discount_price_krw.toLocaleString()}`
                    : course.price_krw
                    ? `₩${course.price_krw.toLocaleString()}`
                    : "무료"}
                </span>
                {course.rating && (
                  <span className="text-yellow-500">
                    ⭐ {course.rating.toFixed(1)}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                수강생: {course.student_count.toLocaleString()}명
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-600">등록된 강의가 없습니다.</p>
      )}
    </div>
  );
}
