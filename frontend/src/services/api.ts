const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface UploadResponse {
  success: boolean
  message: string
  data: {
    name: string
    fileCount: number
  }
}

export async function uploadSubject(name: string, files: FileList): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('name', name)
  
  Array.from(files).forEach((file) => {
    formData.append('files', file)
  })

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('Upload failed')
  }

  return response.json()
} 