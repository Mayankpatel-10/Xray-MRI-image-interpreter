const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="contact" className="bg-medical-900 text-white py-6 px-4">
      <div className="max-w-7xl mx-auto flex items-center justify-center">
        {/* Brand & Copyright */}
        <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 text-center justify-center">
          <h3 className="text-lg font-bold text-medical-400">
            MedScan AI
          </h3>
          <span className="hidden sm:inline text-gray-700">|</span>
          <p className="text-gray-400 text-xs">
            © {currentYear} MedScan AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
