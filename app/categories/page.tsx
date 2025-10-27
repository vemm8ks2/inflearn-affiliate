// app/categories/page.tsx
import { supabase } from "@/lib/supabase";
import Link from "next/link";

export const metadata = {
  title: "카테고리",
  description: "강의 카테고리별 분류",
};

export default async function CategoriesPage() {
  // 카테고리별 강의 수 집계
  const { data: categories } = await supabase
    .from("courses")
    .select("category, subcategory")
    .not("category", "is", null);

  // 카테고리별 그룹화
  const categoryMap = new Map<string, Set<string>>();

  categories?.forEach((item) => {
    if (!item.category) return;

    if (!categoryMap.has(item.category)) {
      categoryMap.set(item.category, new Set());
    }

    if (item.subcategory) {
      categoryMap.get(item.category)!.add(item.subcategory);
    }
  });

  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-3xl font-bold mb-8">카테고리</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from(categoryMap.entries()).map(([category, subcategories]) => (
          <div key={category} className="border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">{category}</h2>
            <ul className="space-y-2">
              {Array.from(subcategories).map((sub) => (
                <li key={sub}>
                  <Link
                    href={`/courses?category=${category}&subcategory=${sub}`}
                    className="text-primary-600 hover:underline"
                  >
                    {sub}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {categoryMap.size === 0 && (
        <p className="text-gray-600">등록된 카테고리가 없습니다.</p>
      )}
    </div>
  );
}
