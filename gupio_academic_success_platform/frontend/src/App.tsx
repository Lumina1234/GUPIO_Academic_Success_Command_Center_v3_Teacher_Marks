import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Activity, ArrowRight, BookOpen, BrainCircuit, ChartNoAxesCombined, CheckCircle2, CircleUserRound, ClipboardList, GraduationCap, LogOut, ShieldCheck, Sparkles, Target, UsersRound } from 'lucide-react';
import { CohortStudent, Metrics, User, Analysis, login, logout, restoreSession, getCoachMe, evaluateCoach, getCohort, simulateCohort, getModelInfo, predict, ModelInfo, Prediction, reportWrongMark, getManagedStudents, updateStudentMarks, createStudent, uploadMarksPDF, getMarkReports, resolveMarkReport, ManagedStudent, MarkReport } from './api';

const featureLabels: Record<string,string> = {
  'Marital status':'Marital status','Application mode':'Application mode','Application order':'Application order','Course':'Course','Daytime/evening attendance':'Attendance timing','Previous qualification':'Previous qualification','Previous qualification (grade)':'Previous qualification grade','Nacionality':'Nationality',"Mother's qualification":"Mother's qualification","Father's qualification":"Father's qualification","Mother's occupation":"Mother's occupation","Father's occupation":"Father's occupation","Admission grade":"Admission grade","Displaced":"Displaced","Educational special needs":"Educational special needs","Debtor":"Debtor","Tuition fees up to date":"Tuition fees up to date","Gender":"Gender","Scholarship holder":"Scholarship holder","Age at enrollment":"Age at enrollment","International":"International","Unemployment rate":"Unemployment rate","Inflation rate":"Inflation rate","GDP":"GDP"
};

function App() {
  const [user, setUser] = useState<User|null>(null);
  const [loginError, setLoginError] = useState('');
  const [view, setView] = useState<'overview'|'coach'|'cohort'|'marks'|'ml'|'security'>('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => { restoreSession().then(setUser).catch(() => {}).finally(() => setLoading(false)); }, []);
  if (loading) return <div className="boot"><div className="spinner"/>Loading secure workspace…</div>;
  if (!user) return <LoginScreen onLogin={async (e,p,o)=>{ try { setLoginError(''); setUser(await login(e,p,o)); } catch(err) { setLoginError(err instanceof Error ? err.message : 'Unable to sign in'); } }} error={loginError}/>;

  return <Dashboard user={user} view={view} setView={setView} onLogout={async()=>{await logout(); setUser(null)}}/>;
}

function LoginScreen({onLogin,error}:{onLogin:(e:string,p:string,o?:string)=>Promise<void>;error:string}) {
  const [role,setRole]=useState<'student'|'teacher'|'admin'>('student');
  const [email,setEmail]=useState('student@gupio.local');
  const [password,setPassword]=useState('ChangeMe!23456789');
  const [otp,setOtp]=useState('');
  const [showPass,setShowPass]=useState(false);

  const selectRole=(r:'student'|'teacher'|'admin')=>{
    setRole(r);
    setEmail(r+'@gupio.local');
    setPassword('ChangeMe!23456789');
    setOtp('');
  };

  const features=[
    {icon:<ChartNoAxesCombined size={20}/>,title:'Predict Outcomes',desc:'Dropout / Enrolled / Graduate'},
    {icon:<UsersRound size={20}/>,title:'Teacher Tools',desc:'Manage marks & track progress'},
    {icon:<Target size={20}/>,title:'Student Support',desc:'Personalized academic guidance'},
    {icon:<ShieldCheck size={20}/>,title:'Secure & Private',desc:'Role-based access & data protection'},
  ];

  return <div className="lp-shell">
    <div className="lp-hero">
      <div className="lp-nav">
        <div className="lp-logo"><div className="lp-logo-icon"><GraduationCap size={20}/></div><div><div className="lp-logo-title">GUPIO <span>ML</span></div><div className="lp-logo-sub">Academic Success Command Center</div></div></div>
        <div className="lp-nav-links"><span>Predict</span><span className="lp-dot">·</span><span>Support</span><span className="lp-dot">·</span><span>Empower</span></div>
      </div>
      <div className="lp-hero-body">
        <h1 className="lp-headline">From Data to<br/><span>Brighter Futures</span></h1>
        <p className="lp-sub">AI-powered insights to help students succeed,<br/>teachers support better, and institutions grow.</p>
        <div className="lp-features">
          {features.map(f=><div className="lp-feat" key={f.title}><div className="lp-feat-icon">{f.icon}</div><div><div className="lp-feat-title">{f.title}</div><div className="lp-feat-desc">{f.desc}</div></div></div>)}
        </div>
      </div>
      <div className="lp-building-bg"/>
    </div>

    <div className="lp-card-wrap">
      <div className="lp-card">
        <div className="lp-card-title">Welcome Back</div>
        <div className="lp-card-sub">Sign in to your Gupio ML account to continue</div>

        <div className="lp-role-row">
          {(['student','teacher','admin'] as const).map(r=><button key={r} className={`lp-role-btn${role===r?' active':''}`} onClick={()=>selectRole(r)}>
            {r==='student'?<CircleUserRound size={22}/>:r==='teacher'?<UsersRound size={22}/>:<ShieldCheck size={22}/>}
            <span>{r.charAt(0).toUpperCase()+r.slice(1)}</span>
          </button>)}
        </div>

        <div className="lp-field">
          <label>Email Address</label>
          <div className="lp-input-wrap"><span className="lp-input-icon"><Activity size={15}/></span><input placeholder="Enter your email" value={email} onChange={e=>setEmail(e.target.value)} autoComplete="username"/></div>
        </div>
        <div className="lp-field">
          <label>Password</label>
          <div className="lp-input-wrap"><span className="lp-input-icon"><ShieldCheck size={15}/></span><input type={showPass?'text':'password'} placeholder="Enter your password" value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password"/><button className="lp-eye" onClick={()=>setShowPass(!showPass)}><Target size={15}/></button></div>
        </div>
        {role==='admin'&&<div className="lp-field"><label>Admin OTP <span style={{color:'#7083b0',fontWeight:400}}>(6-digit code)</span></label><div className="lp-input-wrap"><span className="lp-input-icon"><ShieldCheck size={15}/></span><input value={otp} onChange={e=>setOtp(e.target.value)} placeholder="Enter TOTP code" inputMode="numeric"/></div></div>}

        {error&&<div className="error-box" style={{marginBottom:'12px'}}>{error}</div>}

        <button className="lp-signin-btn" onClick={()=>onLogin(email,password,otp)}>Sign In</button>
        <div className="lp-or"><span>OR</span></div>
        <button className="lp-google-btn"><svg width="18" height="18" viewBox="0 0 48 48"><path fill="#FFC107" d="M43.6 20H24v8h11.3C33.7 33.1 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34 6.5 29.3 4 24 4 12.95 4 4 12.95 4 24s8.95 20 20 20c11 0 20-8 20-20 0-1.3-.1-2.7-.4-4z"/><path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.6 16 19 13 24 13c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34 6.5 29.3 4 24 4 16.4 4 9.7 8.4 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-1.9 13.5-5l-6.2-5.2C29.3 35.3 26.8 36 24 36c-5.2 0-9.6-2.9-11.3-7H6.5C9.8 39.5 16.4 44 24 44z"/><path fill="#1976D2" d="M43.6 20H24v8h11.3c-.8 2.2-2.3 4.1-4.2 5.4l6.2 5.2C41.2 35.2 44 30 44 24c0-1.3-.1-2.7-.4-4z"/></svg>Continue with Google</button>
        <div className="lp-footer">Don't have an account? <span>Contact your institution</span></div>
      </div>
    </div>
  </div>;
}


function Dashboard({user,view,setView,onLogout}:{user:User;view:string;setView:(v:any)=>void;onLogout:()=>Promise<void>}) {
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand-mark side-brand"><div className="brand-icon"><BrainCircuit size={20}/></div><div><div className="brand-title">GUPIO ML</div><div className="brand-sub">Success command</div></div></div>
      <nav>
        <NavItem active={view==='overview'} icon={<ChartNoAxesCombined size={18}/>} label="Overview" onClick={()=>setView('overview')}/>
        <NavItem active={view==='coach'} icon={<Sparkles size={18}/>} label="My Success Coach" onClick={()=>setView('coach')}/>
        {(user.role==='teacher'||user.role==='admin') && <><NavItem active={view==='cohort'} icon={<UsersRound size={18}/>} label="Cohort Simulator" onClick={()=>setView('cohort')}/><NavItem active={view==='marks'} icon={<ClipboardList size={18}/>} label="Marks & Reports" onClick={()=>setView('marks')}/></>} 
        <NavItem active={view==='ml'} icon={<BrainCircuit size={18}/>} label="Enrollment ML" onClick={()=>setView('ml')}/>
        <NavItem active={view==='security'} icon={<ShieldCheck size={18}/>} label="Security" onClick={()=>setView('security')}/>
      </nav>
      <div className="side-bottom"><div className="mini-profile"><div className="avatar">{user.email.slice(0,1).toUpperCase()}</div><div><strong>{user.email}</strong><span>{user.role}</span></div></div><button className="ghost-btn" onClick={onLogout}><LogOut size={16}/> Logout</button></div>
    </aside>
    <main className="main-area">
      <header className="topbar"><div><span className="eyebrow">{user.role.toUpperCase()} WORKSPACE</span><h2>{viewTitle(view)}</h2></div><div className="status-pill"><span className="status-dot"/> Secure session active</div></header>
      {view==='overview' && <Overview go={setView}/>} 
      {view==='coach' && <Coach role={user.role}/>}
      {view==='cohort' && (user.role==='teacher'||user.role==='admin') && <Cohort/>}
      {view==='marks' && (user.role==='teacher'||user.role==='admin') && <MarksReports/>}
      {view==='ml' && <EnrollmentML/>}
      {view==='security' && <SecurityPanel/>}
    </main>
  </div>
}

function NavItem({active,icon,label,onClick}:{active:boolean;icon:ReactNode;label:string;onClick:()=>void}) { return <button className={`nav-item ${active?'active':''}`} onClick={onClick}>{icon}<span>{label}</span></button> }
function viewTitle(v:string){ return ({overview:'Academic overview',coach:'Student success coach',cohort:'Class intervention simulator',marks:'Marks & reports',ml:'Enrollment outcome predictor',security:'Security center'} as any)[v] || 'Academic overview'; }

function Overview({go}:{go:(v:any)=>void}) {
  const [coach,setCoach]=useState<{analysis:Analysis}|null>(null); const [cohort,setCohort]=useState<CohortStudent[]|null>(null);
  useEffect(()=>{ getCoachMe().then(setCoach).catch(()=>{}); getCohort().then(r=>setCohort(r.students)).catch(()=>{}); },[]);
  const atRisk = cohort?.filter(s=>s.analysis.projected_score<40).length ?? 0;
  const onTrack = cohort?.filter(s=>s.analysis.projected_score>=40).length ?? 0;
  const readiness = coach?.analysis.readiness_score ?? 0;
  return <div className="content-grid">
    <section className="hero-card card wide"><div><span className="eyebrow">ACADEMIC EARLY WARNING</span><h1>See who needs help <span>before the exam.</span></h1><p>The command center combines enrollment-time ML with a separate semester coaching layer. Teachers can test support scenarios and turn weak marks into specific teaching actions.</p><div className="hero-actions"><button className="primary-btn" onClick={()=>go('coach')}>Open my coach <ArrowRight size={17}/></button><button className="secondary-btn" onClick={()=>go('cohort')}>Simulate class support</button></div></div><div className="hero-orb"><Target size={80}/><div className="orb-caption">Outcome<br/>intelligence</div></div></section>
    <StatCard label="My readiness" value={`${readiness}%`} sub="Current semester coaching score" icon={<GraduationCap size={18}/>} />
    <StatCard label="Class at risk" value={cohort?String(atRisk):'—'} sub="Scenario readiness below pass threshold" icon={<Activity size={18}/>} />
    <StatCard label="Projected on track" value={cohort?String(onTrack):'—'} sub="Current demo cohort" icon={<CheckCircle2 size={18}/>} />
    <section className="card wide"><div className="section-title"><div><span className="eyebrow">INTERVENTION LOOP</span><h3>How the website solves the problem</h3></div><div className="badge"><ShieldCheck size={14}/> Separate leakage-safe layers</div></div><div className="flow-row"><FlowStep n="01" title="Predict" text="Enrollment ML predicts Dropout / Enrolled / Graduate."/><FlowStep n="02" title="Measure" text="Semester coach reads previous + current performance."/><FlowStep n="03" title="Simulate" text="Teacher tests targeted support and attendance recovery."/><FlowStep n="04" title="Teach" text="Weak areas become a practical action plan."/></div></section>
  </div>
}

function StatCard({label,value,sub,icon}:{label:string;value:string;sub:string;icon:ReactNode}) { return <div className="card stat-card"><div className="stat-icon">{icon}</div><div><span className="muted">{label}</span><strong>{value}</strong><p>{sub}</p></div></div> }
function FlowStep({n,title,text}:{n:string;title:string;text:string}) { return <div className="flow-step"><div className="step-no">{n}</div><h4>{title}</h4><p>{text}</p></div> }

function Coach({role}:{role:string}){
  const [metrics,setMetrics]=useState<Metrics|null>(null);
  const [analysis,setAnalysis]=useState<Analysis|null>(null);
  const [loading,setLoading]=useState(true);
  const [reportField,setReportField]=useState('current_internal_1');
  const [reportReason,setReportReason]=useState('');
  const [reportMsg,setReportMsg]=useState('');
  useEffect(()=>{ getCoachMe().then(r=>{setMetrics(r.metrics);setAnalysis(r.analysis)}).catch(()=>{}).finally(()=>setLoading(false)); },[]);
  const run=async()=>{ if(metrics) setAnalysis(await evaluateCoach(metrics)); };
  const report=async()=>{ try{ setReportMsg(''); await reportWrongMark(reportField,reportReason); setReportReason(''); setReportMsg('Report submitted to the teacher for verification.'); }catch(err){ setReportMsg(err instanceof Error?err.message:'Unable to submit report'); } };
  if(!metrics) return <div className="content-grid"><section className="card"><div className="empty">{loading?'Loading your teacher-entered academic record…':'Academic record unavailable.'}</div></section></div>;
  const metricRows:[keyof Metrics,string][]=[
    ['previous_semester_average','Previous semester average'],['current_internal_1','Current internal 1'],['current_internal_2','Current internal 2'],['assignment_score','Assignment score'],['lab_score','Lab score'],['attendance_pct','Attendance %'],['backlogs','Backlogs'],['pass_threshold','Pass threshold']
  ];
  return <div className="content-grid two">
    <section className="card"><div className="section-title"><div><span className="eyebrow">STUDENT VIEW</span><h3>Your semester record</h3></div><div className="badge purple"><ShieldCheck size={14}/> Teacher entered</div></div>
      <p className="intro">These academic values are entered and maintained by your teacher. Students cannot edit marks or attendance from this portal.</p>
      <div className="metric-form read-only-metrics">{metricRows.map(([key,label])=><div className="compact-field metric-readonly" key={key}><span>{label}</span><strong>{metrics[key]}</strong></div>)}</div>
      {role==='student' && <div className="report-card"><div><span className="eyebrow">CORRECTION REQUEST</span><h4>See a wrong mark?</h4><p className="intro">Choose the field and explain what looks incorrect. Your teacher will verify the official record and make any correction.</p></div>
        <label className="compact-field"><span>Affected field</span><select value={reportField} onChange={e=>setReportField(e.target.value)}>{metricRows.map(([key,label])=><option value={key} key={key}>{label}</option>)}</select></label>
        <label className="compact-field"><span>What is wrong?</span><textarea value={reportReason} onChange={e=>setReportReason(e.target.value)} placeholder="Example: Internal 1 shown here does not match the teacher-announced mark." rows={4}/></label>
        <button className="secondary-btn full" onClick={report} disabled={reportReason.trim().length<5}>Report incorrect mark <ClipboardList size={16}/></button>
        {reportMsg && <div className={reportMsg.startsWith('Report submitted')?'success-box':'error-box'}>{reportMsg}</div>}
      </div>}
    </section>
    <section className="card coach-result">{analysis ? <><div className="result-top"><div><span className="eyebrow">CURRENT READINESS</span><div className="big-score">{analysis.readiness_score}<small>/100</small></div><div className="status-chip">{analysis.status}</div></div><div className="ring"><div><strong>{analysis.pass_probability}%</strong><span>scenario pass</span></div></div></div><div className="score-bar"><span style={{width:(analysis.projected_score)+'%'}}/></div><div className="result-grid"><div><span className="muted">Projected score</span><strong>{analysis.projected_score}</strong></div><div><span className="muted">Support needed</span><strong>{analysis.support_needed}</strong></div></div><div className="subsection"><h4>Weak areas</h4><div className="chip-row">{analysis.weak_areas.length?analysis.weak_areas.map(x=><span className="soft-chip" key={x}>{x}</span>):<span className="soft-chip good">No critical weak area</span>}</div></div><div className="subsection"><h4>Teaching actions</h4>{analysis.teaching_actions.map(x=><div className="action-line" key={x}><CheckCircle2 size={16}/><span>{x}</span></div>)}</div><div className="note"><ShieldCheck size={15}/>{analysis.scenario_note}</div><button className="primary-btn full" onClick={run}>{loading?'Refreshing…':'Refresh success plan'} <Sparkles size={17}/></button></>:<div className="empty">No coaching result available.</div>}</section>
  </div>
}

function Cohort(){
  const [students,setStudents]=useState<CohortStudent[]>([]); const [support,setSupport]=useState(5); const [attendance,setAttendance]=useState(3); const [simulation,setSimulation]=useState<any>(null); const [selected,setSelected]=useState<string|null>(null);
  useEffect(()=>{getCohort().then(r=>setStudents(r.students)).catch(()=>{})},[]);
  const run=async()=>setSimulation(await simulateCohort({support_marks:support,attendance_uplift:attendance}));
  const selectedStudent=students.find(s=>s.public_ref===selected);
  return <div className="content-grid two">
    <section className="card wide"><div className="section-title"><div><span className="eyebrow">TEACHER MODE</span><h3>Class readiness map</h3></div><div className="badge"><UsersRound size={14}/> Cohort controls</div></div><div className="table-wrap"><table><thead><tr><th>Student</th><th>Prev.</th><th>Current</th><th>Attendance</th><th>Readiness</th><th>Status</th></tr></thead><tbody>{students.map(s=><tr key={s.public_ref} onClick={()=>setSelected(s.public_ref)}><td><strong>{s.name}</strong><span>{s.section}</span></td><td>{s.previous_semester_average}</td><td>{Math.round((s.current_internal_1+s.current_internal_2+s.assignment_score+s.lab_score)/4)}</td><td>{s.attendance_pct}%</td><td><div className="mini-bar"><span style={{width:(s.analysis.readiness_score)+'%'}}/></div>{s.analysis.readiness_score}</td><td><span className={`status-dot-chip ${s.analysis.projected_score>=40?'ok':'risk'}`}>{s.analysis.status}</span></td></tr>)}</tbody></table></div></section>
    <section className="card"><span className="eyebrow">SUPPORT SCENARIO</span><h3>What if we help?</h3><p className="intro">Increase selected academic components by a small amount and model the change. This is an educational what-if—not causal proof.</p><div className="slider-block"><div><span>Targeted mark support</span><strong>+{support}</strong></div><input type="range" min={0} max={15} value={support} onChange={e=>setSupport(Number(e.target.value))}/></div><div className="slider-block"><div><span>Attendance recovery</span><strong>+{attendance}%</strong></div><input type="range" min={0} max={10} value={attendance} onChange={e=>setAttendance(Number(e.target.value))}/></div><button className="primary-btn full" onClick={run}>Run class simulation <ChartNoAxesCombined size={17}/></button>{simulation&&<div className="scenario-grid"><div><span className="muted">Pass now</span><strong>{simulation.baseline_pass_count}/{simulation.total_students}</strong></div><div><span className="muted">Pass with support</span><strong>{simulation.supported_pass_count}/{simulation.total_students}</strong></div><div className="highlight"><span className="muted">Additional students</span><strong>+{simulation.additional_students_reaching_threshold}</strong></div></div>}{selectedStudent&&<div className="student-drill"><div className="mini-profile"><div className="avatar">{selectedStudent.name[0]}</div><div><strong>{selectedStudent.name}</strong><span>Section {selectedStudent.section}</span></div></div><div className="drill-score"><strong>{selectedStudent.analysis.readiness_score}</strong><span>readiness</span></div><p>{selectedStudent.analysis.teaching_actions[0]}</p></div>}</section>
  </div>
}

function MarksReports(){
  const [students,setStudents]=useState<ManagedStudent[]>([]);
  const [reports,setReports]=useState<MarkReport[]>([]);
  const [selected,setSelected]=useState<number|null>(null);
  const [draft,setDraft]=useState<(Metrics & {display_name:string;email:string})|null>(null);
  const [status,setStatus]=useState('');
  const [showAdd,setShowAdd]=useState(false);
  const [newS,setNewS]=useState({email:'',display_name:'',program:'AI & Data Science',year:1,course_duration_years:3,previous_semester_average:0,current_internal_1:0,current_internal_2:0,assignment_score:0,lab_score:0,attendance_pct:0,backlogs:0,pass_threshold:40});
  const [addStatus,setAddStatus]=useState('');
  const [uploadStatus,setUploadStatus]=useState('');
  const [isVerifying,setIsVerifying]=useState(false);
  
  const load=async()=>{ const [a,b]=await Promise.all([getManagedStudents(),getMarkReports()]); setStudents(a.students); setReports(b.reports); };
  useEffect(()=>{load().catch(()=>{})},[]);
  const openStudent=(student:ManagedStudent)=>{setSelected(student.student_user_id); setDraft({...student}); setStatus(''); setShowAdd(false); setUploadStatus(''); setIsVerifying(false);};
  const save=async()=>{if(!selected||!draft)return; try{await updateStudentMarks(selected,{year:draft.year,course_duration_years:draft.course_duration_years,year1_average:draft.year1_average,year2_average:draft.year2_average,year3_average:draft.year3_average,previous_semester_average:draft.previous_semester_average,current_internal_1:draft.current_internal_1,current_internal_2:draft.current_internal_2,assignment_score:draft.assignment_score,lab_score:draft.lab_score,attendance_pct:draft.attendance_pct,backlogs:draft.backlogs,pass_threshold:draft.pass_threshold}); setStatus('Marks saved on the server.'); setIsVerifying(false); await load();}catch(err){setStatus(err instanceof Error?err.message:'Unable to save marks')}};
  const resolve=async(id:number,action:'approve'|'reject')=>{try{await resolveMarkReport(id,action,action==='approve'?'Verified by teacher and processed.':'Reviewed by teacher; correction was not approved.'); await load();}catch(err){setStatus(err instanceof Error?err.message:'Unable to resolve report')}};
  const addStudent=async()=>{try{setAddStatus(''); await createStudent(newS); setAddStatus('Student added successfully.'); setNewS({email:'',display_name:'',program:'AI & Data Science',year:1,course_duration_years:3,previous_semester_average:0,current_internal_1:0,current_internal_2:0,assignment_score:0,lab_score:0,attendance_pct:0,backlogs:0,pass_threshold:40}); setShowAdd(false); await load();}catch(err){setAddStatus(err instanceof Error?err.message:'Failed to add student')}};
  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length || !selected || !draft) return;
    setUploadStatus('Uploading and parsing PDF...');
    try {
      const res = await uploadMarksPDF(selected, e.target.files[0]);
      setDraft({...draft, ...res.extracted});
      setUploadStatus('');
      setIsVerifying(true);
    } catch (err) {
      setUploadStatus(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  return <div className="content-grid two">
    <section className="card wide"><div className="section-title"><div><span className="eyebrow">TEACHER / ADMIN</span><h3>Mark register</h3></div><div style={{display:'flex',gap:'8px'}}><button className="small-btn" onClick={()=>{setShowAdd(!showAdd);setDraft(null);setStatus('')}}><GraduationCap size={14}/> Add student</button><div className="badge"><ClipboardList size={14}/> Staff only</div></div></div><p className="intro">Teachers enter the official student marks. Student accounts are strictly read-only and can only submit correction reports.</p>
    {showAdd&&<div className="editor-panel"><div className="section-title"><div><span className="eyebrow">NEW STUDENT</span><h4>Add student account</h4></div></div><div className="metric-form"><label className="compact-field"><span>Email address</span><input type="email" placeholder="student@example.com" value={newS.email} onChange={e=>setNewS({...newS,email:e.target.value})}/></label><label className="compact-field"><span>Full name</span><input type="text" placeholder="Student Name" value={newS.display_name} onChange={e=>setNewS({...newS,display_name:e.target.value})}/></label><label className="compact-field"><span>Program</span><input type="text" value={newS.program} onChange={e=>setNewS({...newS,program:e.target.value})}/></label><label className="compact-field"><span>Current year</span><input type="number" min={1} max={10} value={newS.year} onChange={e=>setNewS({...newS,year:Number(e.target.value)})}/></label><label className="compact-field"><span>Course duration (years)</span><input type="number" min={1} max={10} value={newS.course_duration_years} onChange={e=>setNewS({...newS,course_duration_years:Number(e.target.value)})}/></label>{(['previous_semester_average','current_internal_1','current_internal_2','assignment_score','lab_score','attendance_pct','backlogs','pass_threshold'] as (keyof typeof newS)[]).filter(k=>typeof newS[k]==='number').map(k=><label className="compact-field" key={k}><span>{String(k).split('_').join(' ')}</span><input type="number" min={0} max={k==='backlogs'?20:100} value={newS[k] as number} onChange={e=>setNewS({...newS,[k]:Number(e.target.value)})}/></label>)}</div><div className="hero-actions"><button className="primary-btn" onClick={addStudent}><CheckCircle2 size={16}/> Create student</button><button className="secondary-btn" onClick={()=>setShowAdd(false)}>Cancel</button></div>{addStatus&&<div className={addStatus.startsWith('Student added')?'success-box':'error-box'}>{addStatus}</div>}</div>}
    <div className="table-wrap"><table><thead><tr><th>Student</th><th>Email</th><th>Year</th><th>Prev.</th><th>Internal 1</th><th>Internal 2</th><th>Attendance</th><th>Action</th></tr></thead><tbody>{students.length?students.map(s=><tr key={s.student_user_id}><td><strong>{s.display_name}</strong><span>{s.program}</span></td><td>{s.email}</td><td>{s.year}/{s.course_duration_years}</td><td>{s.previous_semester_average}</td><td>{s.current_internal_1}</td><td>{s.current_internal_2}</td><td>{s.attendance_pct}%</td><td><button className="small-btn" onClick={()=>openStudent(s)}>Edit marks</button></td></tr>):<tr><td colSpan={8} style={{textAlign:'center',padding:'24px',opacity:.5}}>No students yet — use "Add student" to get started.</td></tr>}</tbody></table></div>
    {draft&&<div className="editor-panel">
      <div className="section-title">
        <div><span className="eyebrow">EDITING RECORD</span><h4>{draft.display_name}</h4><span className="muted">{draft.email}</span></div>
        <div style={{display:'flex', gap:'8px', alignItems:'center'}}>
          <label className="small-btn" style={{cursor:'pointer', margin:0}}>
            Upload PDF <input type="file" accept="application/pdf" style={{display:'none'}} onChange={handlePdfUpload} />
          </label>
          <div className="badge green">Server-side record</div>
        </div>
      </div>
      {uploadStatus && <div className="muted" style={{padding:'8px 0'}}>{uploadStatus}</div>}
      {isVerifying && <div className="badge orange" style={{marginBottom:'16px', padding:'8px'}}>PDF parsed! The fields have been auto-filled below. Please verify the extracted values before saving.</div>}
      <div className="metric-form">{(['year','course_duration_years','year1_average','year2_average','year3_average','previous_semester_average','current_internal_1','current_internal_2','assignment_score','lab_score','attendance_pct','backlogs','pass_threshold'] as (keyof Metrics)[]).map(k=><label className="compact-field" key={k}><span>{k.split('_').join(' ')}</span><input type="number" min={0} max={k==='backlogs'?20:k.includes('year')&&!k.includes('average')?10:100} value={draft[k]??''} onChange={e=>setDraft({...draft,[k]:e.target.value===''?null:Number(e.target.value)})}/></label>)}</div>
      <div className="hero-actions"><button className="primary-btn" onClick={save}>{isVerifying ? 'Verify & Save' : 'Save official marks'} <CheckCircle2 size={16}/></button><button className="secondary-btn" onClick={()=>setDraft(null)}>Cancel</button></div>{status&&<div className={status.startsWith('Marks saved')?'success-box':'error-box'}>{status}</div>}
    </div>}
    </section>
    <section className="card"><div className="section-title"><div><span className="eyebrow">STUDENT REPORTS</span><h3>Incorrect mark reports</h3></div><div className="badge orange">{reports.filter(r=>r.status==='open').length} open</div></div><div className="report-list">{reports.length?reports.map(r=><div className="report-item" key={r.id}><div className="report-head"><strong>{r.student_name}</strong><span className={`status-dot-chip ${r.status==='open'?'risk':'ok'}`}>{r.status}</span></div><div className="muted">{r.field_name.split('_').join(' ')} · current value {r.current_value}</div><p>{r.reason}</p>{r.status==='open'&&<div className="hero-actions"><button className="small-btn" onClick={()=>resolve(r.id,'approve')}>Verify &amp; approve</button><button className="small-btn danger" onClick={()=>resolve(r.id,'reject')}>Reject</button></div>}</div>):<div className="empty">No correction reports yet.</div>}</div></section>
  </div>
}



function EnrollmentML(){
  const [info,setInfo]=useState<ModelInfo|null>(null); const [values,setValues]=useState<Record<string,number|null>>({}); const [prediction,setPrediction]=useState<Prediction|null>(null); const [error,setError]=useState('');
  useEffect(()=>{getModelInfo().then(r=>{setInfo(r); const seed:Record<string,number|null>={}; r.features.forEach(f=>seed[f]=null); setValues(seed)}).catch(err=>setError(err.message));},[]);
  const run=async()=>{ try{setError(''); setPrediction(await predict(values))}catch(err){setError(err instanceof Error?err.message:'Prediction failed')}};
  const allFilled = info?.features?.every(f => values[f] !== null && values[f] !== undefined) ?? false;
  return <div className="content-grid two"><section className="card wide"><div className="section-title"><div><span className="eyebrow">GUPIO CORE MODEL</span><h3>Enrollment-time outcome predictor</h3></div><div className={`badge ${info?.trained?'green':'orange'}`}>{info?.trained?<><CheckCircle2 size={14}/> Model trained</>:<>Waiting for data.csv</>}</div></div>{info?.features?.length?<div className="feature-grid">{info.features.map(f=><label className="compact-field" key={f}><span>{featureLabels[f]??f}</span><input type="number" value={values[f]??''} onChange={e=>setValues({...values,[f]:e.target.value===''?null:Number(e.target.value)})}/></label>)}</div>:<div className="empty">{info?.trained===false?'Add the panel-supplied data.csv to data/ and run python -m ml.train to activate the real model.':'Loading model schema…'}</div>}<button className="primary-btn full" onClick={run} disabled={!info?.trained || !allFilled}>Run enrollment prediction <BrainCircuit size={17}/></button>{error&&<div className="error-box">{error}</div>}</section><section className="card">{prediction?<><span className="eyebrow">PREDICTION</span><div className="prediction-word">{prediction.prediction}</div><div className="prob-list">{Object.entries(prediction.probabilities).map(([k,v])=><div key={k}><div className="prob-label"><span>{k}</span><strong>{Math.round(v*100)}%</strong></div><div className="prob-bar"><span style={{width:(v*100)+'%'}}/></div></div>)}</div><div className="note"><ShieldCheck size={15}/>{prediction.interpretation_note} Received {prediction.features_received}/{prediction.features_total} fields.</div></>:<div className="empty"><BrainCircuit size={34}/><p>Run the enrollment model after training the supplied dataset.</p></div>}</section></div>
}

function SecurityPanel(){ return <div className="content-grid two"><section className="card"><span className="eyebrow">SECURITY LOOP</span><h3>Controls built into the application</h3>{[['HTTPS/TLS','Use secure cookie + production HSTS + reverse proxy redirect.'],['Authentication','Argon2 password hash + opaque server-side sessions.'],['Access control','Student sees own profile; teacher/admin only see cohort tools.'],['MFA','Admin requires TOTP.'],['Rate limiting','Login attempts limited per IP and email.'],['Input protection','Pydantic validation + ORM queries + CSP.'],['Audit logging','Auth, coaching, cohort and ML actions are logged.'],['Backups/WAF','Deployment configs and operational checklist are included.']].map(([a,b])=><div className="security-item" key={a}><CheckCircle2 size={17}/><div><strong>{a}</strong><span>{b}</span></div></div>)}</section><section className="card"><span className="eyebrow">IMPORTANT BOUNDARY</span><h3>Why semester marks are separate from ML</h3><p className="intro">The Gupio primary task requires an enrollment-time classifier and explicitly forbids first/second-semester performance variables in that model. The success-coach layer therefore remains a separate transparent scenario engine.</p><div className="boundary"><BookOpen size={18}/><div><strong>Core model</strong><p>Dropout / Enrolled / Graduate from enrollment-time information.</p></div></div><div className="boundary"><Sparkles size={18}/><div><strong>Teaching layer</strong><p>Previous + current semester marks, attendance and intervention scenarios.</p></div></div></section></div> }

export default App;
