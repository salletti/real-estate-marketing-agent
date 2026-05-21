import { Routes, Route, Navigate } from 'react-router-dom'
import NewPublicationPage from '@/pages/NewPublicationPage'
import DraftReviewPage from '@/pages/DraftReviewPage'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<Navigate to="/new" replace />} />
        <Route path="/new" element={<NewPublicationPage />} />
        <Route path="/drafts/:threadId" element={<DraftReviewPage />} />
      </Routes>
    </div>
  )
}
