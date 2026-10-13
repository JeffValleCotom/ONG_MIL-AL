import LoginForm from '../components/LoginForm'
import './LoginPage.css'

function LoginPage() {
  function handleLoginSubmit() {
    // La validación real de credenciales se implementará en TASK-09.
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <header className="login-card__header">
          <p className="login-card__eyebrow">
            ONG MIL-AL
          </p>

          <h1>Iniciar sesión</h1>

          <p>
            Ingresa tus credenciales institucionales para acceder
            a la plataforma de seguimiento integral.
          </p>
        </header>

        <LoginForm
          onSubmit={handleLoginSubmit}
        />

        <footer className="login-card__footer">
          <p>
            El acceso está disponible únicamente para usuarios
            autorizados de MIL-AL.
          </p>
        </footer>
      </section>
    </main>
  )
}

export default LoginPage