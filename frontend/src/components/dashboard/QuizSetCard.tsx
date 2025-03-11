'use client'

import React from 'react';

// Define the props type for your component
interface QuizSetCardProps {
  id: number;
  title: string;
  questionCount: number;
  createdAt: string;
  onClick?: () => void;
}

const QuizSetCard: React.FC<QuizSetCardProps> = ({
  id,
  title,
  questionCount,
  createdAt,
  onClick,
}) => {
  return (
    <div 
      className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="text-gray-600">{questionCount} questions</p>
      <p className="text-gray-500 text-sm">Created: {createdAt}</p>
    </div>
  );
};

export default QuizSetCard;