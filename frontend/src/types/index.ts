export interface VersionInfo {
  version_name: string;
  year: number;
  major_version: number;
  revision: string;
  process_id?: number;
  is_connected: boolean;
  is_mock: boolean;
}

export interface DetectedInstallation {
  year: number;
  major_version: number;
  install_path?: string;
  executable_path?: string;
  is_running: boolean;
  process_id?: number;
  sp_info?: string;
}

export interface ConnectionStatus {
  connected: boolean;
  mode: string;
  active_version?: VersionInfo;
  detected_installations: DetectedInstallation[];
  active_document?: string;
  message: string;
}

export interface MassProperties {
  volume_mm3: number;
  mass_g: number;
  density_g_per_mm3: number;
  surface_area_mm2: number;
  center_of_gravity_mm: [number, number, number];
  material_name: string;
}

export interface FeatureInfo {
  name: string;
  type_name: string;
  suppressed: boolean;
}

export interface DimensionInfo {
  name: string;
  value_mm: number;
  full_name: string;
}

export interface AgentStep {
  step_number: number;
  name: string;
  status: string;
  details: string;
  data: Record<string, any>;
}

export interface SkillEvaluationResult {
  skill_name: string;
  status: string;
  summary: string;
  calculations: Record<string, any>;
  recommendations: string[];
  cad_parameters: Record<string, any>;
  warnings: string[];
}

export interface AgentResponse {
  reply: string;
  active_skill: string;
  skill_evaluation?: SkillEvaluationResult;
  steps: AgentStep[];
  cad_result?: any;
  mass_properties?: MassProperties;
  warnings: string[];
  active_document?: string;
}

export interface ValidationCheck {
  category: string;
  name: string;
  status: 'PASS' | 'FAIL' | 'WARNING' | 'SKIPPED';
  value: string;
  threshold: string;
  details: string;
}

export interface MaterialProperties {
  name: string;
  category: string;
  density_kg_m3: number;
  density_g_cm3: number;
  yield_strength_mpa: number;
  elastic_modulus_gpa: number;
  description: string;
}
