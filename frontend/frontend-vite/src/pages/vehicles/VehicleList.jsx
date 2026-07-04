import React, { useState, useEffect } from 'react';
import api from '../../api/api';
import { useNavigate } from 'react-router-dom';
import { Button, Card, CardContent, Typography, Grid, Container, Alert } from '@mui/material';
const VehicleList = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  // Fetch vehicles on component mount
  useEffect(() => {
    api.get('/api/vehicles')
      .then((response) => {
        setVehicles(response.data);
        setLoading(false);
      })
      .catch((error) => {
        setError('There was an error fetching vehicles!');
        setLoading(false);
      });
  }, []);
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ paddingTop: 3, background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)', minHeight: '100vh' }}>
        <Typography variant="h4" component="h1" gutterBottom style={{ color: '#0052CC' }}>
          Vehicle List
        </Typography>
        <Alert severity="info">Loading vehicles...</Alert>
      </Container>
    );
  }
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ paddingTop: 3, background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)', minHeight: '100vh' }}>
        <Typography variant="h4" component="h1" gutterBottom style={{ color: '#0052CC' }}>
          Vehicle List
        </Typography>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  return (
    <Container maxWidth="lg" sx={{ paddingTop: 3, background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)', minHeight: '100vh' }}>
      <Typography variant="h4" component="h1" gutterBottom style={{ color: '#0052CC' }}>
        Vehicle List
      </Typography>
      <Button
        variant="contained"
        onClick={() => navigate('/vehicles/add')}
        sx={{ marginBottom: 2, backgroundColor: '#0052CC', color: 'white', '&:hover': { backgroundColor: '#003d99' } }}
      >
        Add Vehicle
      </Button>
      {vehicles.length === 0 ? (
        <Alert severity="info">No vehicles available. Please add a vehicle.</Alert>
      ) : (
        <Grid container spacing={3}>
          {vehicles.map((vehicle) => (
            <Grid item xs={12} sm={6} md={4} key={vehicle.id}>
              <Card sx={{ maxWidth: 345 }}>
                <CardContent>
                  <Typography variant="h5" component="div">
                    {vehicle.make} {vehicle.model}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Year: {vehicle.year}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Mileage: {vehicle.mileage} km
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Status: {vehicle.status}
                  </Typography>
                  <Button
                    variant="outlined"
                    sx={{ marginTop: 2, color: '#0052CC', borderColor: '#0052CC', '&:hover': { backgroundColor: '#f0f5ff', borderColor: '#0052CC' } }}
                    onClick={() => navigate(`/vehicles/${vehicle.id}`)}
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};
export default VehicleList;
