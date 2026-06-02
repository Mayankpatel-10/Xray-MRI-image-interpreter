import { HeartPulse, ShieldCheck, Clock, Users, AlertTriangle } from 'lucide-react';

const About = () => {
  const features = [
    {
      icon: HeartPulse,
      title: 'AI-Powered Diagnosis',
      description: 'Our deep learning neural networks analyze medical imaging scans with high accuracy to identify abnormalities.',
    },
    {
      icon: ShieldCheck,
      title: 'Fast & Reliable',
      description: 'Generate diagnostic reports within seconds to assist clinicians with rapid triage and screening decisions.',
    },
    {
      icon: Clock,
      title: '24/7 Support',
      description: 'Access the automated diagnostic tools at any time, providing continuous imaging analysis whenever needed.',
    },
    {
      icon: Users,
      title: 'Clinical Assistant',
      description: 'Designed to serve as a supportive second-opinion helper tool, working alongside healthcare professionals.',
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
            MedScan AI leverages state-of-the-art deep learning architectures to streamline clinical imaging workflows, accelerate preliminary screening, and improve patient care pathways.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, index) => (
            <div
              key={index}
              className="p-6 rounded-2xl bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 hover:shadow-md transition-all duration-300"
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
              MedScan AI was developed to address the growing demand for rapid, accessible, and high-quality medical image analysis. We aim to:
            </p>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-medical-600 mt-2 flex-shrink-0"></div>
                <span className="text-gray-600 dark:text-gray-300">
                  Provide immediate preliminary screenings for time-sensitive clinical cases.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-medical-600 mt-2 flex-shrink-0"></div>
                <span className="text-gray-600 dark:text-gray-300">
                  Act as a reliable, automated diagnostic second opinion to check doctor findings.
                </span>
              </li>
              <li className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-medical-600 mt-2 flex-shrink-0"></div>
                <span className="text-gray-600 dark:text-gray-300">
                  Reduce clinical diagnostic queues and delays in resource-constrained medical centers.
                </span>
              </li>
            </ul>
          </div>
          <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-md rounded-3xl p-8 border border-white/60 dark:border-gray-700/60 shadow-sm">
            <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              AI in Clinical Practice
            </h4>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Our models are trained on thousands of verified medical scans to recognize subtle patterns that might escape standard visual inspection, acting as an extra pair of eyes.
            </p>
            <p className="text-gray-600 dark:text-gray-300">
              By pointing out regions of interest and generating confidence metrics, MedScan AI helps doctors prioritize urgent pathology cases and improve overall screening throughput.
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-amber-50/70 dark:bg-yellow-950/20 backdrop-blur-sm border border-amber-200/50 dark:border-yellow-900/30 rounded-2xl p-6">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-yellow-200 dark:bg-yellow-800">
              <AlertTriangle className="w-6 h-6 text-yellow-800 dark:text-yellow-200" />
            </div>
            <div>
              <h4 className="text-lg font-semibold text-yellow-900 dark:text-yellow-200 mb-2">
                Medical Disclaimer
              </h4>
              <p className="text-yellow-800 dark:text-yellow-300 text-sm">
                MedScan AI is designed for research, screening, and educational purposes. It is <strong className="font-extrabold text-red-600 dark:text-red-400 underline uppercase tracking-wider">NOT</strong> a medical device and is <strong className="font-extrabold text-red-600 dark:text-red-400 underline uppercase tracking-wider">NOT</strong> a substitute for professional clinical judgment, diagnosis, or patient care. Always consult a qualified healthcare provider.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
