'use client'

import QuizSetCard from '@/components/dashboard/QuizSetCard';

// Mock data for quiz sets (you'll replace this with real data later)
const mockQuizSets = [
  { id: 1, title: 'Math Quiz', questionCount: 10, createdAt: '2023-10-15' },
  { id: 2, title: 'Science Quiz', questionCount: 15, createdAt: '2023-10-16' },
  { id: 3, title: 'History Quiz', questionCount: 12, createdAt: '2023-10-17' },
];

export default function Dashboard() {
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Your Quiz Sets</h1>
        <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded flex items-center">
          <span>Upload New Quiz Set</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mockQuizSets.map((quizSet) => (
          <QuizSetCard
            key={quizSet.id}
            id={quizSet.id}
            title={quizSet.title}
            questionCount={quizSet.questionCount}
            createdAt={quizSet.createdAt}
            onClick={() => console.log(`Clicked on quiz set ${quizSet.id}`)}
          />
        ))}
      </div>
    </div>
  );
}