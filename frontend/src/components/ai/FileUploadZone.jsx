import {useRef} from 'react';
export default function FileUploadZone({onFile}){const ref=useRef(); return <div className="drop" onClick={()=>ref.current.click()}><input ref={ref} hidden type="file" accept=".txt,.eml,.pdf,.docx" onChange={e=>e.target.files[0]&&onFile(e.target.files[0])}/><strong>Drop complaint document</strong><span>PDF, DOCX, EML, TXT up to 10MB</span></div>}
