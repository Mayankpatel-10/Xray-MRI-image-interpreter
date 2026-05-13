import { Github, Twitter, Linkedin, Mail, Heart } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    {
      name: 'GitHub',
      icon: Github,
      href: '#',
    },
    {
      name: 'Twitter',
      icon: Twitter,
      href: '#',
    },
    {
      name: 'LinkedIn',
      icon: Linkedin,
      href: '#',
    },
    {
      name: 'Email',
      icon: Mail,
      href: 'mailto:contact@medscan.ai',
    },
  ];

  return (
    <footer id="contact" className="bg-medical-900 text-white py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <h3 className="text-2xl font-bold text-medical-400 mb-4">
              MedScan AI
            </h3>
            <p className="text-gray-400 text-sm">
              AI-powered medical image diagnosis platform helping healthcare professionals
              make faster, more accurate decisions.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-400">
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
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Connect With Us</h4>
            <div className="flex gap-4">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  className="p-2 rounded-lg bg-gray-800 hover:bg-medical-600 transition-colors"
                  aria-label={social.name}
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-400 text-sm">
            © {currentYear} MedScan AI. All rights reserved.
          </p>
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            Built with
            <Heart className="w-4 h-4 text-red-500 fill-red-500" />
            using React
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
