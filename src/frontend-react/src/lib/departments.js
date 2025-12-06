const RAW_DEPARTMENTS = [
  { slug: 'internal_medicine', label: 'Internal Medicine', apiValue: 'internal medicine' },
  { slug: 'surgery', label: 'Surgery', apiValue: 'surgery' },
  { slug: 'ob_gyn_nicu', label: 'OB/GYN/NICU', apiValue: 'ob/gyn/nicu' },
  { slug: 'radiology_imaging', label: 'Radiology/Imaging', apiValue: 'radiology/imaging' },
  { slug: 'outpatient_er', label: 'Outpatient/ER', apiValue: 'outpatient/ER' },
];

const normalize = (value) => {
  if (!value) return '';
  let normalized = value.toString().trim().toLowerCase();
  ['_', '-', '/'].forEach((char) => {
    normalized = normalized.replaceAll(char, ' ');
  });
  return normalized.replace(/\s+/g, ' ');
};

const slugByNormalized = new Map();
RAW_DEPARTMENTS.forEach((dept) => {
  slugByNormalized.set(normalize(dept.slug), dept.slug);
  slugByNormalized.set(normalize(dept.apiValue), dept.slug);
});

const apiBySlug = RAW_DEPARTMENTS.reduce((acc, dept) => {
  acc[dept.slug] = dept.apiValue;
  return acc;
}, {});

export const DEPARTMENTS = RAW_DEPARTMENTS;

export function departmentSlugToApi(value) {
  if (!value) return null;
  const normalized = normalize(value);
  const slug = slugByNormalized.get(normalized);
  if (slug && apiBySlug[slug]) {
    return apiBySlug[slug];
  }
  return value;
}

export function departmentApiToSlug(value) {
  if (!value) return '';
  const normalized = normalize(value);
  return slugByNormalized.get(normalized) || '';
}

export function getDepartmentLabel(value) {
  if (!value || value === 'unspecified') {
    return 'Unspecified';
  }
  const slug = departmentApiToSlug(value) || value;
  const match = DEPARTMENTS.find((dept) => dept.slug === slug);
  return match ? match.label : value;
}
