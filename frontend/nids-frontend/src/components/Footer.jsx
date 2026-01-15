export default function Footer() {
    return (
      <footer className="fixed bottom-0 left-0 w-full bg-[#0f2027] text-white border-t border-white/10 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row justify-between items-center">
          {/* Left: Copyright */}
          <p className="text-sm text-gray-400">
            &copy; {new Date().getFullYear()} NIDS Dashboard. All rights reserved.
          </p>
  
          {/* Right: Links */}
          <div className="flex space-x-6 mt-2 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-[#00fff7] transition-colors text-sm">Privacy</a>
            <a href="#" className="text-gray-400 hover:text-[#00fff7] transition-colors text-sm">Terms</a>
            <a href="#" className="text-gray-400 hover:text-[#00fff7] transition-colors text-sm">Contact</a>
          </div>
        </div>
      </footer>
    );
  }
  