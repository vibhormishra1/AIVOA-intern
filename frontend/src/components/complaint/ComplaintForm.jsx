import { useSelector, useDispatch } from 'react-redux';
import { updateField } from '../../store/slices/complaintSlice';

const sections = [
  ['1. ORIGIN & CUSTOMER DETAILS', ['complaint_source', 'customer_name']],
  ['2. PRODUCT & BATCH IDENTIFICATION', ['product_name', 'product_strength', 'batch_lot_number', 'manufacturing_date', 'expiry_date', 'quantity_affected']],
  ['3. FACILITY & MATERIAL IMPACT', ['complaint_type', 'complaint_date']],
  ['4. DEFECT ANALYSIS', ['initial_severity', 'description']]
];

const labels = {
  complaint_source: 'Complaint Source', customer_name: 'Customer Name',
  product_name: 'Product Name', product_strength: 'Product Strength',
  batch_lot_number: 'Batch / Lot Number', manufacturing_date: 'Manufacturing Date',
  expiry_date: 'Expiry Date', quantity_affected: 'Affected Quantity',
  complaint_type: 'Complaint Category', complaint_date: 'Complaint Date',
  description: 'Complaint Description', initial_severity: 'Severity (Suggested)',
  priority: 'Suggested Next Action'
};

export default function ComplaintForm({ onSave, savedId }) {
  const { formData, submitStatus } = useSelector(s => s.complaint);
  const dispatch = useDispatch();
  const set = (name, value) => dispatch(updateField({ name, value }));

  return (
    <main className="formcard">
      <header className="formhead">
        <div>
          <h1>Log Customer Complaint</h1>
          <p>API & FDF Quality Assurance Module</p>
        </div>
        <span className={`status-badge ${savedId ? 'ready' : 'pending'}`}>
          {savedId ? 'Ready to Commit' : 'Pending Triage'}
        </span>
      </header>

      {sections.map(([title, fields]) => (
        <section className="formsection" key={title}>
          <h3>{title}</h3>
          <div className="grid">
            {fields.map(f => f === 'description' ? (
              <label className="wide" key={f}>
                {labels[f]}
                <textarea 
                  value={formData[f] || ''} 
                  onChange={e => set(f, e.target.value)} 
                  placeholder="Awaiting AI extraction..."
                />
              </label>
            ) : (
              <label key={f}>
                {labels[f]}
                <input 
                  type={f.includes('date') ? 'date' : 'text'} 
                  value={formData[f] || ''} 
                  onChange={e => set(f, e.target.value)} 
                  placeholder="Awaiting AI extraction..."
                />
              </label>
            ))}
          </div>
        </section>
      ))}
      
      <button 
        className="primary-btn" 
        onClick={() => onSave(formData)} 
        disabled={submitStatus === 'loading'}
      >
        {submitStatus === 'loading' ? 'Committing...' : 'Commit to QMS Ledger'}
      </button>
    </main>
  );
}
