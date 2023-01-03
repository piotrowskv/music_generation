import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import { ThemeProvider } from './stores/ThemeContext'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
    <ThemeProvider>
        <HashRouter>
            <App />
        </HashRouter>
    </ThemeProvider>
)
