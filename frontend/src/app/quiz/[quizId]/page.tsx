'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { useRouter } from 'next/navigation'

// Sample quiz following your MongoDB schema
const sampleQuiz = {
  id: "quiz_123",
  subject_ids: ["math_101", "algebra_basics"],
  user_id: "user_456",
  status: "not_started", // "not_started" | "in_progress" | "complete"
  score: null,
  questions: [
    {
      id: "q1",
      question: "What is the value of x in the equation 2x + 4 = 10?",
      choices: ["2", "3", "4", "5"],
      correct_choice: 1  // index of correct answer (3)
    },
    {
      id: "q2",
      question: "If y = 3x + 2, what is y when x = 4?",
      choices: ["10", "12", "14", "16"],
      correct_choice: 2  // index of correct answer (14)
    },
    {
      id: "q3",
      question: "What is the square root of 64?",
      choices: ["6", "7", "8", "9"],
      correct_choice: 2  // index of correct answer (8)
    }
  ],
  state: [], // Will be populated as user answers questions
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
}

export default function QuizPage() {
  const router = useRouter()
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [quizState, setQuizState] = useState<Array<{ question_id: string; answer: number | null }>>(
    sampleQuiz.questions.map(q => ({ question_id: q.id, answer: null }))
  )
  const [status, setStatus] = useState<'not_started' | 'in_progress' | 'complete'>('not_started')
  const [score, setScore] = useState<number | null>(null)

  const currentQuestion = sampleQuiz.questions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / sampleQuiz.questions.length) * 100

  const handleStartQuiz = () => {
    setStatus('in_progress')
  }

  const handleAnswerSelect = (value: string) => {
    setQuizState(prev => {
      const newState = [...prev]
      newState[currentQuestionIndex].answer = parseInt(value)
      return newState
    })
  }

  const calculateScore = () => {
    const correctAnswers = quizState.reduce((count, answer, index) => {
      return count + (answer.answer === sampleQuiz.questions[index].correct_choice ? 1 : 0)
    }, 0)
    return Math.round((correctAnswers / sampleQuiz.questions.length) * 100)
  }

  const handleNext = () => {
    if (currentQuestionIndex < sampleQuiz.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    } else {
      const finalScore = calculateScore()
      setScore(finalScore)
      setStatus('complete')
      // Here you would typically send the completed quiz state to your backend
    }
  }

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
    }
  }

  const handleRestart = () => {
    setCurrentQuestionIndex(0)
    setQuizState(sampleQuiz.questions.map(q => ({ question_id: q.id, answer: null })))
    setStatus('not_started')
    setScore(null)
  }

  if (status === 'not_started') {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardHeader>
            <CardTitle>Ready to start the quiz?</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={handleStartQuiz}>Start Quiz</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (status === 'complete') {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardHeader>
            <CardTitle>Quiz Complete!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <p className="text-2xl font-bold mb-2">Your Score</p>
              <p className="text-4xl font-bold text-green-600">{score}%</p>
              <p className="text-sm text-muted-foreground mt-2">
                You got {quizState.reduce((count, answer, index) => 
                  count + (answer.answer === sampleQuiz.questions[index].correct_choice ? 1 : 0), 0
                )} out of {sampleQuiz.questions.length} questions correct
              </p>
            </div>
            
            <div className="flex justify-center gap-4 mt-6">
              <Button variant="outline" onClick={handleRestart}>
                Restart Quiz
              </Button>
              <Button onClick={() => router.push('/dashboard')}>
                Return to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Quiz in Progress</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Question {currentQuestionIndex + 1} of {sampleQuiz.questions.length}</span>
              <span>{Math.round(progress)}% complete</span>
            </div>
            <Progress value={progress} />
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium">{currentQuestion.question}</h3>
            <RadioGroup
              value={quizState[currentQuestionIndex].answer?.toString() || ""}
              onValueChange={handleAnswerSelect}
              className="space-y-2"
            >
              {currentQuestion.choices.map((choice, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <RadioGroupItem value={index.toString()} id={`option-${index}`} />
                  <Label htmlFor={`option-${index}`}>{choice}</Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
            >
              Previous
            </Button>
            <Button
              onClick={handleNext}
              disabled={quizState[currentQuestionIndex].answer === null}
            >
              {currentQuestionIndex === sampleQuiz.questions.length - 1 ? 'Submit' : 'Next'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
