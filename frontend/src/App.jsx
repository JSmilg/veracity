import { Routes, Route } from 'react-router-dom'
import Header from './components/common/Header'
import Footer from './components/common/Footer'
import HomePage from './pages/HomePage'
import LeaderboardPage from './pages/LeaderboardPage'
import JournalistDetailPage from './pages/JournalistDetailPage'
import AboutPage from './pages/AboutPage'
import TransferTimelinePage from './pages/TransferTimelinePage'
import ReliabilityMatrixPage from './pages/ReliabilityMatrixPage'
import ComingSoonPage from './pages/ComingSoonPage'

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      <main className="flex-grow container mx-auto max-w-7xl px-4 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/journalist/:slug" element={<JournalistDetailPage />} />
          <Route path="/transfer/:id" element={<TransferTimelinePage />} />
          <Route path="/matrix" element={<ReliabilityMatrixPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/coming-soon/:domain" element={<ComingSoonPage />} />
        </Routes>
      </main>

      <Footer />
    </div>
  )
}

export default App
