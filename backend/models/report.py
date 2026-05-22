from pymongo import MongoClient
import certifi
from datetime import datetime
import os
from dotenv import load_dotenv
import gridfs

load_dotenv()

class Report:
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI', 'mongodb+srv://medscan:MedScan@medscan.d6wgjyi.mongodb.net/medscan_auth?retryWrites=true&w=majority&appName=MedScan'),
            tlsCAFile=certifi.where()
        )
        self.db = self.client[os.getenv('MONGO_DATABASE', 'medscan_auth')]
        self.reports_collection = self.db.reports
        self.fs = gridfs.GridFS(self.db)
        
    def create_report(self, patient_info, prediction_result, scan_type, pdf_bytes, user_id=None):
        """Create a new report in database"""
        # Store PDF in GridFS
        pdf_id = self.fs.put(pdf_bytes, filename=f"report_{scan_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        # Create report document
        report_doc = {
            'patient_info': patient_info,
            'prediction_result': prediction_result,
            'scan_type': scan_type,
            'pdf_id': pdf_id,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert report
        result = self.reports_collection.insert_one(report_doc)
        
        return {
            'success': True,
            'report_id': str(result.inserted_id),
            'pdf_id': str(pdf_id),
            'message': 'Report created successfully'
        }
    
    def get_report_by_id(self, report_id):
        """Get report by ID"""
        try:
            from bson.objectid import ObjectId
            report = self.reports_collection.find_one({'_id': ObjectId(report_id)})
            if report:
                return {
                    'success': True,
                    'report': report
                }
            else:
                return {'success': False, 'message': 'Report not found'}
        except:
            return {'success': False, 'message': 'Invalid report ID'}
    
    def get_pdf_by_report_id(self, report_id):
        """Get PDF bytes by report ID"""
        try:
            from bson.objectid import ObjectId
            report = self.reports_collection.find_one({'_id': ObjectId(report_id)})
            if report:
                pdf_id = report.get('pdf_id')
                if pdf_id:
                    pdf_data = self.fs.get(pdf_id)
                    return {
                        'success': True,
                        'pdf_bytes': pdf_data.read(),
                        'filename': f"report_{report['scan_type']}_{report['created_at'].strftime('%Y%m%d_%H%M%S')}.pdf"
                    }
                else:
                    return {'success': False, 'message': 'PDF not found in report'}
            else:
                return {'success': False, 'message': 'Report not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_all_reports(self, user_id=None, limit=50):
        """Get all reports, optionally filtered by user"""
        try:
            query = {}
            if user_id:
                query['user_id'] = user_id
            
            reports = []
            for report_doc in self.reports_collection.find(query).sort('created_at', -1).limit(limit):
                reports.append({
                    'id': str(report_doc['_id']),
                    'patient_info': report_doc.get('patient_info', {}),
                    'prediction_result': report_doc.get('prediction_result', {}),
                    'scan_type': report_doc.get('scan_type', 'unknown'),
                    'pdf_id': str(report_doc.get('pdf_id', '')),
                    'user_id': report_doc.get('user_id'),
                    'created_at': report_doc['created_at'],
                    'updated_at': report_doc.get('updated_at')
                })
            
            return reports
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []
    
    def delete_report(self, report_id):
        """Delete report and associated PDF"""
        try:
            from bson.objectid import ObjectId
            report = self.reports_collection.find_one({'_id': ObjectId(report_id)})
            if report:
                # Delete PDF from GridFS
                pdf_id = report.get('pdf_id')
                if pdf_id:
                    try:
                        self.fs.delete(pdf_id)
                    except:
                        pass
                
                # Delete report document
                result = self.reports_collection.delete_one({'_id': ObjectId(report_id)})
                
                if result.deleted_count > 0:
                    return {'success': True, 'message': 'Report deleted successfully'}
                else:
                    return {'success': False, 'message': 'Failed to delete report'}
            else:
                return {'success': False, 'message': 'Report not found'}
        except:
            return {'success': False, 'message': 'Failed to delete report'}
    
    def get_report_count(self, user_id=None):
        """Get total number of reports"""
        try:
            query = {}
            if user_id:
                query['user_id'] = user_id
            count = self.reports_collection.count_documents(query)
            return count
        except Exception as e:
            print(f"Error counting reports: {e}")
            return 0
    
    def close_connection(self):
        """Close database connection"""
        self.client.close()
