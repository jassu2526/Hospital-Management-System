import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './index.css';

// --- Auth Context ---
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role');
    const username = localStorage.getItem('username');
    
    if (token && role && username) {
      setUser({ token, role, username });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/api/token/', {
        username,
        password
      });
      const { access, refresh, role, username: resUsername } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_role', role);
      localStorage.setItem('username', resUsername || username);
      setUser({ token: access, role, username: resUsername || username });
      return true;
    } catch (error) {
      console.error("Login failed", error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

const useAuth = () => useContext(AuthContext);

// --- Protected Route ---
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // User doesn't have required role, send to their specific dashboard
    return <Navigate to={`/${user.role.toLowerCase()}`} replace />;
  }
  
  return children;
};

// --- Login Component ---
function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, user } = useAuth();
  const navigate = useNavigate();

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate(`/${user.role.toLowerCase()}`);
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const success = await login(username, password);
    if (success) {
      // The useEffect will handle redirection after user state updates
    } else {
      setError('Invalid username or password');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ width: '48px', height: '48px', background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))', borderRadius: '12px', margin: '0 auto 16px' }}></div>
          <h1 style={{ fontSize: '1.75rem' }}>Welcome to <span className="text-gradient">CareMatrix</span></h1>
          <p style={{ color: 'var(--text-secondary)' }}>Please log in to your account</p>
        </div>
        
        {error && <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '12px', borderRadius: '8px', marginBottom: '16px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>{error}</div>}
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none' }}
              required
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none' }}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ marginTop: '8px', padding: '12px' }}>Log In</button>
        </form>
      </div>
    </div>
  );
}

// --- Dashboards ---

function AdminDashboard() {
  const { user } = useAuth();
  return (
    <>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Admin Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome back, {user?.username}. Overview of hospital operations.</p>
      </header>
      <div className="dashboard-grid">
        <div className="glass-panel stat-card">
          <span className="stat-title">System Users</span>
          <span className="stat-value">256</span>
          <span style={{ color: '#10b981', fontSize: '0.875rem' }}>↑ 5 new today</span>
        </div>
        <div className="glass-panel stat-card">
          <span className="stat-title">Hospitals</span>
          <span className="stat-value">3</span>
        </div>
      </div>
    </>
  );
}

function DoctorDashboard() {
  const { user } = useAuth();
  return (
    <>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Doctor Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome back, Dr. {user?.username}. Here is your schedule.</p>
      </header>
      <div className="glass-panel">
        <h2>Today's Appointments</h2>
        <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
          <h4>10:30 AM</h4>
          <p style={{ color: 'var(--text-secondary)' }}>Patient Jane Doe - General Checkup</p>
        </div>
      </div>
    </>
  );
}

function PatientDashboard() {
  const { user } = useAuth();
  const [hospitals, setHospitals] = useState([]);
  const [selectedHospital, setSelectedHospital] = useState('');
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [reason, setReason] = useState('');
  const [appointments, setAppointments] = useState([]);
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

  // Fetch Hospitals and existing appointments on mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [hospRes, apptRes] = await Promise.all([
          axios.get('http://localhost:8000/hospital/api/hospitals/', {
            headers: { Authorization: `Bearer ${user.token}` }
          }),
          axios.get('http://localhost:8000/appointments/api/patient/', {
            headers: { Authorization: `Bearer ${user.token}` }
          })
        ]);
        setHospitals(hospRes.data);
        setAppointments(apptRes.data);
      } catch (err) {
        console.error("Error fetching data", err);
      }
    };
    fetchInitialData();
  }, [user.token]);

  // Fetch doctors when hospital changes
  useEffect(() => {
    if (selectedHospital) {
      axios.get(`http://localhost:8000/accounts/api/doctors/?hospital_id=${selectedHospital}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      })
        .then(res => setDoctors(res.data))
        .catch(err => console.error(err));
    } else {
      setDoctors([]);
    }
  }, [selectedHospital, user.token]);

  // Group doctors by category (specialization)
  const groupedDoctors = doctors.reduce((acc, doc) => {
    const category = doc.specialization || 'General';
    if (!acc[category]) acc[category] = [];
    acc[category].push(doc);
    return acc;
  }, {});

  const handleBookAppointment = async (e) => {
    e.preventDefault();
    setStatusMsg({ type: '', text: '' });
    try {
      const payload = {
        hospital: selectedHospital,
        date,
        time,
        notes: reason
      };
      if (selectedDoctor) {
        payload.doctor = selectedDoctor;
      }
      const res = await axios.post('http://localhost:8000/appointments/api/patient/', payload, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setAppointments([res.data, ...appointments]);
      setStatusMsg({ type: 'success', text: 'Appointment booked successfully!' });
      // Reset form
      setSelectedHospital('');
      setSelectedDoctor('');
      setDate('');
      setTime('');
      setReason('');
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Failed to book appointment. Please check all fields.' });
    }
  };

  return (
    <>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Patient Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome back, {user?.username}. Manage your health and bookings.</p>
      </header>

      <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        
        {/* Booking Form */}
        <div className="glass-panel">
          <h2 style={{ marginBottom: '24px' }}>Book an Appointment</h2>
          {statusMsg.text && (
            <div style={{ 
              background: statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
              color: statusMsg.type === 'success' ? '#10b981' : '#ef4444', 
              padding: '12px', borderRadius: '8px', marginBottom: '16px', border: '1px solid currentColor' 
            }}>
              {statusMsg.text}
            </div>
          )}
          
          <form onSubmit={handleBookAppointment} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Select Hospital</label>
              <select 
                value={selectedHospital} 
                onChange={(e) => { setSelectedHospital(e.target.value); setSelectedDoctor(''); }}
                style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none' }}
                required
              >
                <option value="">-- Choose a Hospital --</option>
                {hospitals.map(h => (
                  <option key={h.id} value={h.id}>{h.name} ({h.city})</option>
                ))}
              </select>
            </div>

            {selectedHospital && (
              <div>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Select Doctor (Optional)</label>
                <select 
                  value={selectedDoctor} 
                  onChange={(e) => setSelectedDoctor(e.target.value)}
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none' }}
                >
                  <option value="">-- Any Available Doctor --</option>
                  {Object.entries(groupedDoctors).map(([category, docs]) => (
                    <optgroup key={category} label={category}>
                      {docs.map(d => (
                        <option key={d.id} value={d.id}>
                          Dr. {d.user?.first_name || ''} {d.user?.last_name || d.user?.username}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>
            )}

            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Date</label>
                <input 
                  type="date" 
                  value={date} 
                  onChange={(e) => setDate(e.target.value)}
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none', colorScheme: 'dark' }}
                  required
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Time</label>
                <input 
                  type="time" 
                  value={time} 
                  onChange={(e) => setTime(e.target.value)}
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none', colorScheme: 'dark' }}
                  required
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Reason for Visit</label>
              <textarea 
                value={reason} 
                onChange={(e) => setReason(e.target.value)}
                rows="3"
                style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)', color: 'white', outline: 'none' }}
                required
              ></textarea>
            </div>

            <button type="submit" className="btn btn-primary" style={{ padding: '14px', marginTop: '8px' }}>
              Confirm Booking
            </button>
          </form>
        </div>

        {/* Appointments List */}
        <div className="glass-panel">
          <h2 style={{ marginBottom: '24px' }}>My Appointments</h2>
          {appointments.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No upcoming appointments.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {appointments.map(appt => (
                <div key={appt.id} style={{ padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', borderLeft: appptStatusColor(appt.status) }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <h4 style={{ margin: 0 }}>{appt.doctor ? `Dr. ${appt.doctor?.user?.username || appt.doctor_id}` : 'General / Any Doctor'}</h4>
                    <span style={{ fontSize: '0.8rem', padding: '2px 8px', borderRadius: '12px', background: 'var(--surface-color)' }}>{appt.status}</span>
                  </div>
                  <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    {appt.date} at {appt.time}
                  </p>
                  <p style={{ margin: '8px 0 0', fontSize: '0.85rem' }}>"{appt.notes || 'No reason provided'}"</p>
                </div>
              ))}
            </div>
          )}
        </div>
        
      </div>
    </>
  );
}

function appptStatusColor(status) {
  if (status === 'APPROVED') return '4px solid #10b981';
  if (status === 'REJECTED') return '4px solid #ef4444';
  return '4px solid #f59e0b'; // PENDING
}

function AttendantDashboard() {
  const { user } = useAuth();
  return (
    <>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Attendant Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome back, {user?.username}. Here are your tasks.</p>
      </header>
      <div className="glass-panel">
        <h2>Room Assignments</h2>
        <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
          <h4>ICU Ward A</h4>
          <p style={{ color: 'var(--text-secondary)' }}>Shift: Morning</p>
        </div>
      </div>
    </>
  );
}

// --- Navigation Component ---
function Navigation() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  if (!user) return null; // Don't show nav if not logged in
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))', borderRadius: '8px' }}></div>
        <span className="text-gradient">CareMatrix</span>
      </div>
      <div className="navbar-nav">
        {user.role === 'ADMIN' && <Link to="/admin" className="nav-link">Admin Home</Link>}
        {user.role === 'DOCTOR' && <Link to="/doctor" className="nav-link">My Schedule</Link>}
        {user.role === 'PATIENT' && <Link to="/patient" className="nav-link">My Health</Link>}
        {user.role === 'ATTENDANT' && <Link to="/attendant" className="nav-link">My Shift</Link>}
        <button className="btn btn-secondary" style={{ marginLeft: '16px' }} onClick={handleLogout}>Log Out</button>
      </div>
    </nav>
  );
}

// --- Main App Component ---
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="container">
          <Navigation />
          <main>
            <Routes>
              <Route path="/login" element={<Login />} />
              
              {/* Redirect root to appropriate dashboard */}
              <Route path="/" element={<Navigate to="/login" replace />} />
              
              <Route path="/admin/*" element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              
              <Route path="/doctor/*" element={
                <ProtectedRoute allowedRoles={['DOCTOR']}>
                  <DoctorDashboard />
                </ProtectedRoute>
              } />
              
              <Route path="/patient/*" element={
                <ProtectedRoute allowedRoles={['PATIENT']}>
                  <PatientDashboard />
                </ProtectedRoute>
              } />
              
              <Route path="/attendant/*" element={
                <ProtectedRoute allowedRoles={['ATTENDANT']}>
                  <AttendantDashboard />
                </ProtectedRoute>
              } />
              
              {/* Catch all route */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
