const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="contact" className="bg-medical-900 text-white py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col items-center text-center space-y-8 mb-12">
          {/* Brand */}
          <div className="max-w-2xl">
            <h3 className="text-3xl font-bold text-medical-400 mb-4">
              MedScan AI
            </h3>
            <p className="text-gray-400 text-sm md:text-base leading-relaxed">
              AI-powered medical image diagnosis platform helping healthcare professionals
              make faster, more accurate decisions.
            </p>
          </div>

          {/* Quick Links */}
          <nav>
            <ul className="flex flex-wrap justify-center gap-8 text-gray-400 font-medium">
              <li>
                <a href="#home" className="hover:text-medical-400 transition-colors">
                  Home
                </a>
              </li>
              <li>
                <a href="#upload" className="hover:text-medical-400 transition-colors">
                  Upload
                </a>
              </li>
              <li>
                <a href="#about" className="hover:text-medical-400 transition-colors">
                  About
                </a>
              </li>
              <li>
                <a href="#contact" className="hover:text-medical-400 transition-colors">
                  Contact
                </a>
              </li>
            </ul>
          </nav>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-center items-center gap-4">
          <p className="text-gray-400 text-sm text-center">
            © {currentYear} MedScan AI. All rights reserved by Mayank & Kavya.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

