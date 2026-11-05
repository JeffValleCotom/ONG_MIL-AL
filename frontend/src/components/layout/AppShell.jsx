import { useState } from 'react'

import AppHeader from './AppHeader'
import AppSidebar from './AppSidebar'

import './AppShell.css'


export default function AppShell({
  title,
  subtitle,
  user,
  roleLabel,
  navigationItems = [],
  onChangeSpace,
  onLogout,
  children,
}) {
  const [mobileNavigationOpen, setMobileNavigationOpen] =
    useState(false)

  return (
    <div className="milal-app-shell">
      <div
        className={
          'milal-app-shell__sidebar '
          + (
            mobileNavigationOpen
              ? 'milal-app-shell__sidebar--open'
              : ''
          )
        }
      >
        <AppSidebar
          items={navigationItems}
          onClose={() => {
            setMobileNavigationOpen(false)
          }}
        />
      </div>

      {mobileNavigationOpen && (
        <button
          className="milal-app-shell__overlay"
          type="button"
          aria-label="Cerrar navegación"
          onClick={() => {
            setMobileNavigationOpen(false)
          }}
        />
      )}

      <div className="milal-app-shell__workspace">
        <AppHeader
          title={title}
          subtitle={subtitle}
          user={user}
          roleLabel={roleLabel}
          onMenuOpen={() => {
            setMobileNavigationOpen(true)
          }}
          onChangeSpace={onChangeSpace}
          onLogout={onLogout}
        />

        <main className="milal-app-shell__content">
          {children}
        </main>
      </div>
    </div>
  )
}
