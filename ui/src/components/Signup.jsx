import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Mail, Lock, User, ArrowRight } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const Signup = () => {
  const { isDark } = useTheme();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Authentication will be added later
    console.log('Signup attempt:', formData);
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-medical-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4 py-8">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center gap-2">
            <Activity className="w-10 h-10 text-medical-600 dark:text-medical-400" />
            <span className="text-2xl font-bold text-medical-600 dark:text-medical-400">
              MedScan AI
            </span>
          </div>
        </div>

        {/* Signup Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 text-center">
            Create Account
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-center mb-8">
            Join MedScan AI today
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-medical-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                  placeholder="John Doe"
                />
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-medical-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-medical-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-medical-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-start">
              <input
                type="checkbox"
                required
                className="w-4 h-4 mt-1 text-medical-600 border-gray-300 rounded focus:ring-medical-500"
              />
              <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                I agree to the{' '}
                <a href="#" className="text-medical-600 dark:text-medical-400 hover:underline">
                  Terms of Service
                </a>{' '}
                and{' '}
                <a href="#" className="text-medical-600 dark:text-medical-400 hover:underline">
                  Privacy Policy
                </a>
              </span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full bg-medical-600 hover:bg-medical-700 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              Create Account
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>

          {/* Sign In Link */}
          <p className="mt-8 text-center text-gray-600 dark:text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-medical-600 dark:text-medical-400 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
