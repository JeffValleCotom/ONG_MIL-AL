import milalLogo
  from '../../assets/ong-milal-logo.png'

import './AuthLayout.css'


export default function AuthLayout({
  eyebrow = 'Acceso institucional',
  title,
  description,
  children,
}) {
  return (
    <main className="milal-auth">
      <section className="milal-auth__brand">
        <div className="milal-auth__brand-content">
          <img
            className="milal-auth__logo"
            src={milalLogo}
            alt="ONG MIL-AL"
          />

          <div className="milal-auth__brand-copy">
            <p className="milal-auth__brand-eyebrow">
              ONG MIL-AL
            </p>

            <h1>
              Seguimiento integral para el desarrollo
              de nuestros estudiantes
            </h1>

            <p>
              Plataforma institucional para la gestión,
              acompañamiento y seguimiento de los
              estudiantes de ONG MIL-AL.
            </p>
          </div>
        </div>

        <div
          className="milal-auth__brand-decoration"
          aria-hidden="true"
        >
          <span className="milal-auth__brand-curve milal-auth__brand-curve--green" />
          <span className="milal-auth__brand-curve milal-auth__brand-curve--red" />
        </div>
      </section>

      <section className="milal-auth__workspace">
        <div className="milal-auth__mobile-brand">
          <img
            src={milalLogo}
            alt="ONG MIL-AL"
          />

          <strong>ONG MIL-AL</strong>
        </div>

        <div className="milal-auth__card">
          <header className="milal-auth__card-header">
            <p className="milal-auth__eyebrow">
              {eyebrow}
            </p>

            <h2>{title}</h2>

            {description && (
              <p className="milal-auth__description">
                {description}
              </p>
            )}
          </header>

          <div className="milal-auth__card-content">
            {children}
          </div>
        </div>

        <p className="milal-auth__legal">
          Acceso exclusivo para personal autorizado
          de ONG MIL-AL.
        </p>
      </section>
    </main>
  )
}
