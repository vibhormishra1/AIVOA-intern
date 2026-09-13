import { useDispatch, useSelector } from 'react-redux';
import { submitComplaint, triggerExtraction } from '../store/slices/complaintSlice';
import ComplaintForm from '../components/complaint/ComplaintForm';
import AIIntakePanel from '../components/ai/AIIntakePanel';

export default function ComplaintLogger() {
  const dispatch = useDispatch();
  const c = useSelector(s => s.complaint);
  
  const handleFile = (f) => dispatch(triggerExtraction({ file: f, file_type: f.name.split('.').pop(), file_name: f.name }));
  const handlePaste = (text) => dispatch(triggerExtraction({ file_content: text, file_type: 'txt', file_name: 'pasted.txt' }));
  
  return (
    <div className="workspace">
      <ComplaintForm onSave={data => dispatch(submitComplaint(data))} savedId={c.savedComplaintId} />
      <AIIntakePanel 
        complaintId={c.savedComplaintId} 
        onFile={handleFile} 
        onPaste={v => v.length > 40 && handlePaste(v)} 
        progress={c.extractionProgress} 
        message={c.extractionMessage} 
        metadata={c.aiMetadata} 
        missing={c.missingFields} 
      />
    </div>
  );
}
