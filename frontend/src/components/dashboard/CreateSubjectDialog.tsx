'use client'

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { PlusCircle } from "lucide-react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useState } from "react"
import { toast } from "sonner"
import { uploadSubject } from '@/services/api'

const ACCEPTED_FILE_TYPES = [
  "text/markdown",
  "text/x-markdown",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/msword",
  "text/plain",
  "application/pdf",
  "application/rtf",
  "application/vnd.apple.pages",
  "application/vnd.apple.keynote",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation"
]

const MAX_TOTAL_SIZE = 10 * 1024 * 1024; // 10MB in bytes
const MAX_INDIVIDUAL_SIZE = 3 * 1024 * 1024; // 3MB in bytes

const subjectFormSchema = z.object({
  name: z.string().min(1, "Subject name is required"),
  files: z.any()
    .refine(
      (files) => files?.length > 0, 
      "At least one file is required"
    )
    .refine(
      (files) => Array.from(files ?? []).every((file) => 
        ACCEPTED_FILE_TYPES.includes((file as File).type)
      ),
      "Only .md, .docx, .doc, .txt, .pdf, .rtf, .pages, .key, and .pptx files are allowed"
    )
    .refine(
      (files) => Array.from(files ?? []).every((file) => 
        (file as File).size <= MAX_INDIVIDUAL_SIZE
      ),
      "Each file must be smaller than 1MB"
    )
    .refine(
      (files) => Array.from(files ?? []).reduce<number>(
        (total, file) => total + (file as File).size, 0
      ) <= MAX_TOTAL_SIZE,
      "Total file size must not exceed 10MB"
    )
})

type SubjectFormValues = z.infer<typeof subjectFormSchema>

export default function CreateSubjectDialog() {
  const [isUploading, setIsUploading] = useState(false)
  const form = useForm<SubjectFormValues>({
    resolver: zodResolver(subjectFormSchema),
  })

  async function onSubmit(data: SubjectFormValues) {
    try {
      setIsUploading(true)
      const result = await uploadSubject(data.name, data.files as FileList)
      toast.success('Subject created successfully')
      form.reset()
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to create subject')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <PlusCircle className="h-4 w-4" />
          Create Subject
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Subject</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Subject Name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="files"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Upload Files</FormLabel>
                  <FormControl>
                    <Input 
                      type="file" 
                      multiple 
                      accept=".md,.docx,.doc,.txt,.pdf,.rtf,.pages,.key,.pptx"
                      onChange={(e) => {
                        const files = e.target.files;
                        console.log('File types:', Array.from(files ?? []).map(f => f.type));
                        field.onChange(files);
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button 
              type="submit" 
              className="w-full"
              disabled={isUploading}
            >
              {isUploading ? 'Creating...' : 'Create Subject'}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}