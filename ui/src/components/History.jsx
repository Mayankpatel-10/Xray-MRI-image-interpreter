import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useToast } from './Toast';
import { getReports, deleteReport } from '../services/api';
import authService from '../services/authService';
import { 
  Brain, 
  HeartPulse, 
  Download, 
  Trash2, 
  Calendar, 
  User, 
  ArrowLeft, 
  AlertCircle, 
  Search,
  Filter,
  Clock,
  FileText,
  Loader2
} from 'lucide-react';
import Navbar from './Navbar';
import Footer from './Footer';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const History = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [reportToDelete, setReportToDelete] = useState(null);
  
  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [scanFilter, setScanFilter] = useState('all');

  useEffect(() => {
    // Check if user is authenticated
    if (!authService.isAuthenticated()) {
      addToast('Please login to access your scan history', 'warning');
      navigate('/login');
      return;
    }

    fetchReports();
  }, [navigate]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await getReports();
      setReports(data.reports || []);
    } catch (err) {
      console.error('Failed to load history:', err);
      addToast(err.message || 'Failed to retrieve scan history', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (report) => {
    setReportToDelete(report);
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = async () => {
    if (!reportToDelete) return;
    
    try {
      setDeletingId(reportToDelete.id);
      await deleteReport(reportToDelete.id);
      addToast('Scan record deleted successfully', 'success');
      
      // Update local state
      setReports((prev) => prev.filter((r) => r.id !== reportToDelete.id));
    } catch (err) {
      console.error('Failed to delete report:', err);
      addToast(err.message || 'Failed to delete scan record', 'error');
    } finally {
      setDeletingId(null);
      setShowDeleteConfirm(false);
      setReportToDelete(null);
    }
  };

  // Filter and search reports
  const filteredReports = reports.filter((report) => {
    const matchesSearch = report.patient_name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    
    const matchesScanType = 
      scanFilter === 'all' ||
      (scanFilter === 'brain' && report.scan_type === 'brain') ||
      (scanFilter === 'chest' && report.scan_type === 'chest');

    return matchesSearch && matchesScanType;
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScanBadge = (scanType) => {
    if (scanType === 'brain') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
          <Brain className="w-3.5 h-3.5" />
          Brain MRI
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400 border border-teal-200 dark:border-teal-800">
        <HeartPulse className="w-3.5 h-3.5" />
        Chest X-Ray
      </span>
    );
  };

  const getPredictionBadge = (prediction) => {
    const isNormal = ['NORMAL', 'notumor'].includes(prediction);
    if (isNormal) {
      return (
        <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          Normal / Safe
        </span>
      );
    }
    
    // Format label to uppercase for readability
    const label = prediction.toUpperCase();
    return (
      <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">
        {label}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 flex flex-col transition-colors duration-300">
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-grow pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        {/* Back navigation & Header */}
        <div className="mb-8">
          <Link 
            to="/" 
            className="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-medical-600 dark:hover:text-medical-400 font-medium transition-colors mb-4 group"
          >
            <ArrowLeft className="w-4 h-4 transform group-hover:-translate-x-1 transition-transform" />
            Back to Dashboard
          </Link>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
                Diagnostic History
              </h1>
              <p className="mt-2 text-sm sm:text-base text-gray-600 dark:text-gray-400">
                View, download, and manage your past AI-assisted medical scan analyses.
              </p>
            </div>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="bg-white/75 backdrop-blur-md rounded-3xl border border-white/50 p-4 mb-8 shadow-sm flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="relative w-full sm:max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by patient name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-gray-350 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent transition-all dark:text-white"
            />
          </div>
          
          <div className="flex items-center gap-2 w-full sm:w-auto shrink-0 justify-end">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={scanFilter}
              onChange={(e) => setScanFilter(e.target.value)}
              className="py-2 px-3 text-sm rounded-xl border border-gray-350 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent transition-all dark:text-white cursor-pointer"
            >
              <option value="all">All Scans</option>
              <option value="brain">Brain MRIs Only</option>
              <option value="chest">Chest X-Rays Only</option>
            </select>
          </div>
        </div>

        {/* Results Section */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 text-medical-600 animate-spin" />
            <p className="mt-4 text-gray-500 dark:text-gray-400 font-medium">Retrieving history records...</p>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="text-center py-16 bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-300 dark:border-gray-700 p-8 shadow-sm">
            <Clock className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">No history records found</h3>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
              {searchTerm || scanFilter !== 'all' 
                ? "We couldn't find any results matching your search terms." 
                : "You haven't run any diagnostic scans yet. Upload images from the dashboard to get started!"}
            </p>
            {(searchTerm || scanFilter !== 'all') && (
              <button
                onClick={() => { setSearchTerm(''); setScanFilter('all'); }}
                className="mt-4 inline-flex items-center justify-center px-4 py-2 text-sm font-semibold rounded-xl text-medical-700 bg-medical-50 hover:bg-medical-100 dark:text-medical-400 dark:bg-medical-950/30 dark:hover:bg-medical-950/60 transition-colors"
              >
                Clear filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredReports.map((report) => (
              <div 
                key={report.id}
                className="bg-white/75 backdrop-blur-md rounded-3xl border border-white/40 shadow-sm overflow-hidden flex flex-col justify-between hover:shadow-md hover:border-gray-300 transition-all duration-300 group"
              >
                {/* Card Header */}
                <div className="p-6 pb-4">
                  <div className="flex items-center justify-between gap-2 mb-4">
                    {getScanBadge(report.scan_type)}
                    <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      {formatDate(report.created_at)}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2 mb-4">
                    <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                      <User className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-955 dark:text-white truncate max-w-[200px]">
                        {report.patient_name}
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Patient</p>
                    </div>
                  </div>

                  {/* Diagnostic details */}
                  <div className="bg-gray-50 dark:bg-gray-950 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs text-gray-500 dark:text-gray-400">AI Result:</span>
                      {getPredictionBadge(report.prediction)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500 dark:text-gray-400">Confidence:</span>
                      <span className="text-sm font-extrabold text-medical-600 dark:text-medical-400">
                        {report.confidence}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900/50 border-t border-gray-150 dark:border-gray-800/80 flex items-center gap-3">
                  <a
                    href={`${API_BASE_URL}${report.download_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 inline-flex items-center justify-center gap-2 py-2 px-3 bg-primary-500 hover:bg-primary-600 active:bg-primary-700 text-white text-sm font-bold rounded-xl transition-colors shadow-sm cursor-pointer"
                  >
                    <Download className="w-4 h-4" />
                    Download PDF
                  </a>
                  <button
                    onClick={() => handleDeleteClick(report)}
                    disabled={deletingId === report.id}
                    className="p-2 bg-white hover:bg-red-50 hover:text-red-600 dark:bg-gray-800 dark:hover:bg-red-950/30 dark:hover:text-red-400 border border-gray-250 dark:border-gray-700 hover:border-red-200 dark:hover:border-red-900 text-gray-500 dark:text-gray-400 rounded-xl transition-colors"
                    title="Delete record"
                  >
                    <Trash2 className="w-4.5 h-4.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <Footer />

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white dark:bg-gray-900 rounded-2xl max-w-md w-full p-6 shadow-xl border border-gray-200 dark:border-gray-800 transform scale-100 transition-all">
            <div className="flex items-center gap-3 text-red-600 mb-4">
              <AlertCircle className="w-6 h-6 shrink-0" />
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Delete Diagnostic Scan?</h3>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Are you sure you want to delete the diagnostic report for{' '}
              <strong className="text-gray-900 dark:text-white">
                {reportToDelete?.patient_name}
              </strong>
              ? This action cannot be undone and will permanently remove the record and the associated PDF file.
            </p>
            
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setReportToDelete(null);
                }}
                disabled={deletingId !== null}
                className="px-4 py-2 text-sm font-semibold rounded-xl text-gray-700 bg-gray-100 hover:bg-gray-200 dark:text-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                disabled={deletingId !== null}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-xl text-white bg-red-600 hover:bg-red-700 active:bg-red-800 transition-colors shadow-sm disabled:opacity-50"
              >
                {deletingId ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  'Delete Record'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;
