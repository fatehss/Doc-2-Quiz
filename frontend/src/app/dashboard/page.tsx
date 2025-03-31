'use client'

import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import QuizSetCard from '@/components/dashboard/QuizSetCard';
import { Button } from "@/components/ui/button"
import { PlusCircle } from "lucide-react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import CreateSubjectDialog from '@/components/dashboard/CreateSubjectDialog'

// Mock data for quiz sets (you'll replace this with real data later)
const mockQuizSets = [
  { id: 1, title: 'Math Quiz', questionCount: 10, createdAt: '2023-10-15', subject: 'Mathematics' },
  { id: 2, title: 'Science Quiz', questionCount: 15, createdAt: '2023-10-16', subject: 'Physics' },
  { id: 3, title: 'History Quiz', questionCount: 12, createdAt: '2023-10-17', subject: 'History' },
];

// Mock data (replace with real data later)
const mockSubjects = [
  { id: 1, title: 'Mathematics', description: 'Advanced calculus and algebra' },
  { id: 2, title: 'Physics', description: 'Classical mechanics and thermodynamics' },
  { id: 3, title: 'Chemistry', description: 'Organic and inorganic chemistry' },
];

const quizFormSchema = z.object({
  questionCount: z.number().min(5).max(30).default(10),
  otherInstructions: z.string().optional(),
})

type QuizFormValues = z.infer<typeof quizFormSchema>

// export default function Dashboard() {
//   return (
//     <div>
//       <div className="flex justify-between items-center mb-6">
//         <h1 className="text-3xl font-bold">Your Quiz Sets</h1>
//         <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded flex items-center">
//           <span>Upload New Quiz Set</span>
//         </button>
//       </div>

//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
//         {mockQuizSets.map((quizSet) => (
//           <QuizSetCard
//             key={quizSet.id}
//             id={quizSet.id}
//             title={quizSet.title}
//             questionCount={quizSet.questionCount}
//             createdAt={quizSet.createdAt}
//             onClick={() => console.log(`Clicked on quiz set ${quizSet.id}`)}
//           />
//         ))}
//       </div>
//     </div>
//   );
// }
export default function Dashboard() {
  const form = useForm<QuizFormValues>({
    resolver: zodResolver(quizFormSchema),
    defaultValues: {
      questionCount: 10,
      otherInstructions: "",
    },
  })

  function onSubmit(data: QuizFormValues) {
    // Form submission logic will go here
    console.log(data)
  }

  return (
    <div className="flex flex-col space-y-4 w-full">
      <div className="border border-black rounded-lg p-4 flex justify-center items-center w-full">
        <h1 className="text-2xl font-bold">Dashboard</h1>
      </div>
      
      <div className="border border-black rounded-lg p-4 w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Subjects</h2>
          <CreateSubjectDialog />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockSubjects.map((subject) => (
            <Dialog key={subject.id}>
              <DialogTrigger asChild>
                <Card className="hover:bg-slate-100 cursor-pointer transition-colors">
                  <CardHeader>
                    <CardTitle>{subject.title}</CardTitle>
                  </CardHeader>
                </Card>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Quiz for {subject.title}</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                      control={form.control}
                      name="questionCount"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Number of Questions</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              min={5} 
                              max={30} 
                              {...field} 
                              onChange={e => field.onChange(Number(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="otherInstructions"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Other Instructions (Optional)</FormLabel>
                          <FormControl>
                            <Textarea {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button type="submit" className="w-full">Create Quiz</Button>
                  </form>
                </Form>
              </DialogContent>
            </Dialog>
          ))}
        </div>
      </div>

      <div className="border border-black rounded-lg p-4 w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Quiz Sets</h2>
          <Button variant="outline" className="flex items-center gap-2">
            <PlusCircle className="h-4 w-4" />
            Create Quiz
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockQuizSets.map((quiz) => (
            <Dialog key={quiz.id}>
              <DialogTrigger asChild>
                <Card className="hover:bg-slate-100 cursor-pointer transition-colors">
                  <CardHeader>
                    <CardTitle>{quiz.title}</CardTitle>
                    <div className="text-sm text-muted-foreground">
                      <p>Subject: {quiz.subject}</p>
                      <p>{quiz.questionCount} questions</p>
                      <p>Created: {new Date(quiz.createdAt).toLocaleDateString()}</p>
                    </div>
                  </CardHeader>
                </Card>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>{quiz.title}</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <h4 className="font-medium">Quiz Details</h4>
                    <p>Subject: {quiz.subject}</p>
                    <p>Number of questions: {quiz.questionCount}</p>
                    <p>Created: {new Date(quiz.createdAt).toLocaleDateString()}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button className="w-full">Start Quiz</Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          ))}
        </div>
      </div>
    </div>
  )
}