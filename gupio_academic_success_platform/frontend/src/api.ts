const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

let csrfToken: string | null = null;

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (csrfToken) headers.set('X-CSRF-Token', csrfToken);
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  });
  if (!response.ok) {
    let detail = 'Request failed';
    try { detail = (await response.json()).detail ?? detail; } catch {}
    throw new Error(detail);
  }
  return response.json();
}

export async function login(email: string, password: string, otp?: string) {
  const result = await request<{user: User; csrf_token: string}>('/api/v1/auth/login', {
    method: 'POST', body: JSON.stringify({ email, password, otp: otp || null }),
  });
  csrfToken = result.csrf_token;
  return result.user;
}

export async function restoreSession() {
  const result = await request<{user: User; csrf_token: string}>('/api/v1/auth/me');
  csrfToken = result.csrf_token;
  return result.user;
}

export async function logout() {
  await request('/api/v1/auth/logout', { method: 'POST', body: '{}' });
  csrfToken = null;
}

export async function getProfile() { return request<ProfileResponse>('/api/v1/profile/me'); }
export async function getCoachMe() { return request<CoachMe>('/api/v1/coach/me'); }
export async function evaluateCoach(metrics: Metrics) { return request<Analysis>('/api/v1/coach/evaluate', { method: 'POST', body: JSON.stringify(metrics) }); }
export async function getCohort() { return request<{students: CohortStudent[]}>('/api/v1/coach/cohort'); }
export async function simulateCohort(payload: {support_marks: number; attendance_uplift: number; target_threshold?: number|null}) {
  return request<Simulation>('/api/v1/coach/cohort/simulate', { method: 'POST', body: JSON.stringify(payload) });
}
export async function getModelInfo() { return request<ModelInfo>('/api/v1/ml/model-info'); }
export async function getManagedStudents() { return request<{students: ManagedStudent[]}>('/api/v1/marks/students'); }
export async function updateStudentMarks(studentUserId: number, payload: Metrics) { return request<ManagedStudent>(`/api/v1/marks/students/${studentUserId}`, { method: 'PUT', body: JSON.stringify(payload) }); }
export async function createStudent(payload: {email:string;display_name:string;program:string;year:number;course_duration_years:number;previous_semester_average:number;current_internal_1:number;current_internal_2:number;assignment_score:number;lab_score:number;attendance_pct:number;backlogs:number;pass_threshold:number}) { return request<ManagedStudent>('/api/v1/marks/students', { method: 'POST', body: JSON.stringify(payload) }); }
export async function uploadMarksPDF(studentUserId: number, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return request<{extracted: Partial<Metrics>; warnings: string[]}>(`/api/v1/marks/students/${studentUserId}/upload-pdf`, {
    method: 'POST',
    body: formData,
    headers: {} // Let browser set Content-Type for FormData
  });
}
export async function reportWrongMark(field_name: string, reason: string) { return request<{id:number;status:string}>('/api/v1/marks/reports', { method:'POST', body: JSON.stringify({field_name, reason}) }); }
export async function getMarkReports() { return request<{reports: MarkReport[]}>('/api/v1/marks/reports'); }
export async function resolveMarkReport(reportId:number, action:'approve'|'reject', teacher_note:string) { return request<{id:number;status:string}>(`/api/v1/marks/reports/${reportId}/resolve`, { method:'POST', body: JSON.stringify({action, teacher_note}) }); }
export async function predict(features: Record<string, number | null>) {
  return request<Prediction>('/api/v1/ml/predict', { method: 'POST', body: JSON.stringify({features}) });
}

export type User = { email: string; role: 'student'|'teacher'|'admin'; mfa_enabled: boolean };
export type ProfileResponse = { user: User; profile: null | { display_name: string; program: string; year: number } & Metrics };
export type Metrics = {
  year: number; course_duration_years: number; year1_average: number|null; year2_average: number|null; year3_average: number|null;
  previous_semester_average: number; current_internal_1: number; current_internal_2: number;
  assignment_score: number; lab_score: number; attendance_pct: number; backlogs: number; pass_threshold: number;
};
export type Analysis = { readiness_score: number; projected_score: number; status: string; pass_probability: number; support_needed: string; weak_areas: string[]; teaching_actions: string[]; scenario_note: string };
export type CoachMe = { name: string; metrics: Metrics; analysis: Analysis };
export type ManagedStudent = { student_user_id:number; email:string; display_name:string; program:string; year:number } & Metrics;
export type MarkReport = { id:number; student_user_id:number; student_name:string; student_email:string; field_name:string; current_value:number; reason:string; status:string; teacher_note:string|null; created_at:string; resolved_at:string|null };
export type CohortStudent = { public_ref: string; name: string; section: string; year: number; course_duration_years: number; year1_average: number|null; year2_average: number|null; year3_average: number|null; previous_semester_average: number; current_internal_1: number; current_internal_2: number; assignment_score: number; lab_score: number; attendance_pct: number; backlogs: number; pass_threshold: number; analysis: Analysis };
export type Simulation = { total_students: number; baseline_pass_count: number; supported_pass_count: number; additional_students_reaching_threshold: number; support_marks: number; attendance_uplift: number; note: string; students: Array<{public_ref: string; name: string; baseline: Analysis; supported: Analysis; improved: boolean}> };
export type ModelInfo = { trained: boolean; model_name: string|null; classes: string[]; features: string[]; evaluation?: {test_accuracy: number; test_macro_f1: number; test_rows: number} };
export type Prediction = { prediction: string; probabilities: Record<string, number>; features_received: number; features_total: number; interpretation_note: string };
