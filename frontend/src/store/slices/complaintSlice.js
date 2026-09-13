import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { extractComplaint as requestExtraction, saveComplaint as requestSave } from '../../api/complaintApi';
const localToday = () => { const now = new Date(); return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`; };
const initialForm={complaint_source:'',customer_name:'',product_name:'',product_strength:'',batch_lot_number:'',manufacturing_date:'',expiry_date:'',quantity_affected:'',quantity_unit:'kg',complaint_type:'',complaint_date:localToday(),description:'',initial_severity:'',priority:'',raw_document_text:''};
const hasValue = value => value !== null && value !== undefined && value !== '';
const mergeMeaningfulFields = (current, incoming) => Object.fromEntries(Object.entries(incoming || {}).filter(([, value]) => hasValue(value)));
const appendRawText = (current, next) => next ? [current, next].filter(Boolean).join('\n\n') : current;
export const triggerExtraction=createAsyncThunk('complaint/extract',async(payload)=>(await requestExtraction(payload)).data);
export const submitComplaint=createAsyncThunk('complaint/save',async(payload)=>(await requestSave(payload)).data);
const applyExtraction = (state, data) => {
  const risk = data.risk_classification || {};
  const aiFields = {
    ...data.extracted_fields,
    initial_severity: risk.initial_severity,
    priority: risk.priority,
  };
  state.formData = {
    ...state.formData,
    ...mergeMeaningfulFields(state.formData, aiFields),
    raw_document_text: appendRawText(state.formData.raw_document_text, data.raw_text),
  };
  state.aiMetadata = { risk_classification: risk, capa_suggestions: data.capa_suggestions };
  state.missingFields = data.missing_fields;
  state.extractionStatus = 'complete';
  state.extractionProgress = 100;
  state.extractionMessage = 'Extraction complete';
};
const slice=createSlice({name:'complaint',initialState:{formData:initialForm,extractionStatus:'idle',extractionProgress:0,extractionMessage:'',aiMetadata:null,missingFields:[],submitStatus:'idle',savedComplaintId:null,error:null},reducers:{updateField:(s,a)=>{s.formData[a.payload.name]=a.payload.value},updateFields:(s,a)=>{s.formData={...s.formData,...mergeMeaningfulFields(s.formData,a.payload)}},updateExtractionProgress:(s,a)=>Object.assign(s,a.payload),populateFromAI:(s,a)=>{applyExtraction(s,a.payload)},resetForm:(s)=>{s.formData={...initialForm,complaint_date:localToday()};s.aiMetadata=null;s.missingFields=[];s.savedComplaintId=null;s.submitStatus='idle'}},extraReducers:b=>{b.addCase(triggerExtraction.pending,s=>{s.extractionStatus='processing';s.extractionProgress=15;s.extractionMessage='Analyzing complaint...'}).addCase(triggerExtraction.fulfilled,(s,a)=>{applyExtraction(s,a.payload.data)}).addCase(triggerExtraction.rejected,(s,a)=>{s.extractionStatus='error';s.error=a.error.message;s.extractionProgress=0;s.extractionMessage='Error: ' + a.error.message}).addCase(submitComplaint.pending,s=>{s.submitStatus='loading'}).addCase(submitComplaint.fulfilled,(s,a)=>{s.submitStatus='success';s.savedComplaintId=a.payload.complaint_id}).addCase(submitComplaint.rejected,(s,a)=>{s.submitStatus='error';s.error=a.error.message})}});
export const {updateField,updateFields,updateExtractionProgress,populateFromAI,resetForm}=slice.actions;export default slice.reducer;
