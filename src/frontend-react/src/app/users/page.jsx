'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, hasRole, getUserData } from '@/lib/Common';
import DataService from '@/lib/DataService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertCircle, CheckCircle2, Loader2, Users as UsersIcon, Trash2, Edit, Search } from 'lucide-react';

export default function UsersPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const departments = [
    { value: 'internal_medicine', label: 'Internal Medicine' },
    { value: 'surgery', label: 'Surgery' },
    { value: 'ob_gyn_nicu', label: 'OB/GYN/NICU' },
    { value: 'radiology_imaging', label: 'Radiology/Imaging' },
    { value: 'outpatient_er', label: 'Outpatient/ER' },
  ];

  const roles = [
    { value: 'viewer', label: 'Viewer' },
    { value: 'nurse', label: 'Nurse' },
    { value: 'doctor', label: 'Doctor' },
    { value: 'admin', label: 'Admin' },
  ];

  useEffect(() => {
    if (!isAuthenticated() || !hasRole(['admin'])) {
      router.push('/');
      return;
    }
    const userData = getUserData();
    setUser(userData);
    fetchUsers();
  }, [router]);

  useEffect(() => {
    const filtered = users.filter(u =>
      u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.role.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredUsers(filtered);
  }, [searchTerm, users]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await DataService.Users.listUsers();
      setUsers(response.users || []);
      setFilteredUsers(response.users || []);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (userToEdit) => {
    setEditingUser(userToEdit.username);
    setFormData({
      email: userToEdit.email,
      role: userToEdit.role,
      department: userToEdit.department,
    });
    setError('');
    setSuccess('');
  };

  const handleCancelEdit = () => {
    setEditingUser(null);
    setFormData({});
    setError('');
  };

  const handleUpdate = async (username) => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await DataService.Users.updateUser(username, formData);
      setSuccess(`User ${username} updated successfully`);
      setEditingUser(null);
      setFormData({});
      await fetchUsers();
    } catch (err) {
      console.error('Update error:', err);
      setError(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (username) => {
    if (!confirm(`Are you sure you want to delete user "${username}"?`)) {
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await DataService.Users.deleteUser(username);
      setSuccess(`User ${username} deleted successfully`);
      await fetchUsers();
    } catch (err) {
      console.error('Delete error:', err);
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground mt-2">
            Manage system users and permissions
          </p>
        </div>
        <div className="flex items-center gap-2">
          <UsersIcon className="w-6 h-6 text-primary" />
          <span className="text-2xl font-bold">{users.length}</span>
          <span className="text-sm text-muted-foreground">Total Users</span>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 p-3 rounded-md bg-green-100 text-green-800 text-sm">
          <CheckCircle2 className="w-4 h-4" />
          <span>{success}</span>
        </div>
      )}

      {/* Search */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Search Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search by username, email, or role..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
          <CardDescription>
            {filteredUsers.length} user{filteredUsers.length !== 1 ? 's' : ''} found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading && users.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No users found matching your search
            </div>
          ) : (
            <div className="space-y-4">
              {filteredUsers.map((u) => (
                <div
                  key={u.username}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  {editingUser === u.username ? (
                    // Edit Mode
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-lg">{u.username}</h3>
                        <span className={`role-badge role-${u.role}`}>{u.role}</span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>Email</Label>
                          <Input
                            value={formData.email || ''}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            disabled={loading}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label>Role</Label>
                          <Select
                            value={formData.role || ''}
                            onValueChange={(value) => setFormData({ ...formData, role: value })}
                            disabled={loading}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {roles.map((role) => (
                                <SelectItem key={role.value} value={role.value}>
                                  {role.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <Label>Department</Label>
                          <Select
                            value={formData.department || ''}
                            onValueChange={(value) => setFormData({ ...formData, department: value })}
                            disabled={loading}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {departments.map((dept) => (
                                <SelectItem key={dept.value} value={dept.value}>
                                  {dept.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleUpdate(u.username)}
                          disabled={loading}
                        >
                          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save Changes'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleCancelEdit}
                          disabled={loading}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    // View Mode
                    <div className="flex items-start justify-between">
                      <div className="space-y-2 flex-grow">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-lg">{u.username}</h3>
                          <span className={`role-badge role-${u.role}`}>{u.role}</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                          <div>
                            <span className="text-muted-foreground">Email: </span>
                            <span>{u.email}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Department: </span>
                            <span>
                              {departments.find(d => d.value === u.department)?.label || u.department}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2 ml-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(u)}
                          disabled={loading}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDelete(u.username)}
                          disabled={loading || u.username === user?.username}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
