import Navbar from './Navbar';
import Footer from './Footer';

export default function Layout({ children }) {
    return (
        <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-primary)' }}>
            <Navbar />
            <main style={{ padding: 'var(--space-xl)', paddingTop: 'var(--space-2xl)', paddingBottom: 'var(--space-2xl)' }}>
                {children}
            </main>
            <Footer />
        </div>
    );
}
