import { HeartPulse, ShieldCheck, Clock, Users, AlertTriangle } from 'lucide-react';

const About = () => {
  const features = [
    {
      icon: HeartPulse,
      title: 'AI-Powered Diagnosis',
      description: 'Our advanced deep learning models analyze medical images with high accuracy to assist healthcare professionals.',
    },
    {
      icon: ShieldCheck,
      title: 'Fast & Reliable',
      description: 'Get instant predictions within seconds, enabling quick screening and triage decisions.',
    },
    {
      icon: Clock,
      title: '24/7 Availability',
      description: 'Access our diagnostic tool anytime, anywhere, ensuring continuous support for medical needs.',
    },
    {
      icon: Users,
      title: 'Doctor Support',
      description: 'Designed to assist, not replace, medical professionals in making informed decisions.',
    },
  ];

  return (
    <section id="about" className="py-20 px-4 bg-medical-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            About <span className="text-medical-600 dark:text-medical-400">MedScan AI</span>
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Leveraging artificial intelligence to revolutionize medical image diagnosis and improve patient outcomes.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, index) => (
            <div
              key={index}
              className="p-6 rounded-xl bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 hover:shadow-lg transition-shadow"
            >
              <div className="p-3 rounded-lg bg-medical-100 dark:bg-medical-900/50 w-fit mb-4">
                <feature.icon className="w-6 h-6 text-medical-600 dark:text-medical-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Purpose Section */}
        <div className="grid lg:grid-cols-2 gap-12 items-center mb-16">
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
              Our Purpose
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              MedScan AI was developed to address the growing need for accessible and accurate medical image analysis. 
              By harnessing the power of deep learning, we aim to:
            </p>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-medical-600 mt-2 flex-shrink-0"></div>
                <span className="text-gray-600 dark:text-gray-300">
                  Provide rapid preliminary screening for critical conditions
                </span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-medical-600 mt-2 flex-shrink-0"></div>
                <span className="text-gray-600 dark:text-gray-300">
                  Assist healthcare professionals in making informed decisions
                </span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-medical-600 mt-2 flex-shrink-0"></div>
                <span className="text-gray-600 dark:text-gray-300">
                  Reduce diagnostic delays in resource-constrained areas
                </span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-medical-600 mt-2 flex-shrink-0"></div>
                <span className="text-gray-600 dark:text-gray-300">
                  Improve patient outcomes through early detection
                </span>
              </li>
            </ul>
          </div>
          <div className="bg-medical-50 dark:bg-medical-900/20 rounded-2xl p-8 border-2 border-medical-200 dark:border-medical-800">
            <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              How AI Helps Doctors
            </h4>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Our AI models are trained on thousands of verified medical images to recognize patterns that may be 
              difficult to detect with the human eye. This technology serves as a powerful second opinion tool.
            </p>
            <p className="text-gray-600 dark:text-gray-300">
              By highlighting potential areas of concern and providing confidence scores, MedScan AI enables doctors 
              to focus their expertise where it matters most, ultimately improving diagnostic accuracy and efficiency.
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-yellow-200 dark:bg-yellow-800">
              <AlertTriangle className="w-6 h-6 text-yellow-800 dark:text-yellow-200" />
            </div>
            <div>
              <h4 className="text-lg font-semibold text-yellow-900 dark:text-yellow-200 mb-2">
                Important Disclaimer
              </h4>
              <p className="text-yellow-800 dark:text-yellow-300">
                MedScan AI is intended for research and educational purposes only. It is <strong>not</strong> a replacement 
                for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or 
                other qualified health provider with any questions you may have regarding a medical condition. 
                Never disregard professional medical advice or delay in seeking it because of something you have 
                read or seen on this platform.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
