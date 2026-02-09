import { Link, useLocation } from 'react-router-dom'
import VLogo from './VLogo'

const Header = () => {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <header className="bg-surface-0/90 backdrop-blur-lg border-b border-edge sticky top-0 z-50">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <VLogo />

          <div className="flex items-center space-x-1">
            {[
              { to: '/', label: 'Home' },
              { to: '/leaderboard', label: 'Leaderboard' },
              { to: '/transfer/2', label: 'Transfer Timeline', match: '/transfer/' },
              { to: '/matrix', label: 'Matrix' },
              { to: '/about', label: 'About' },
            ].map(({ to, label, match }) => {
              const active = match ? location.pathname.startsWith(match) : isActive(to)
              return (
                <Link
                  key={to}
                  to={to}
                  className={`relative px-4 py-2 font-sans text-sm font-medium transition-colors duration-200 ${
                    active ? 'text-zinc-100' : 'text-zinc-400 hover:text-zinc-100'
                  }`}
                >
                  {label}
                  {active && (
                    <div className="absolute bottom-0 left-2 right-2 h-0.5 bg-accent rounded-full" />
                  )}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>
    </header>
  )
}

export default Header
