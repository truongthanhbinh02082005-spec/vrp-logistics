import axios from 'axios';

export const geocodeAddress = async (address) => {
    try {
        const response = await axios.get('https://nominatim.openstreetmap.org/search', {
            params: {
                q: address,
                format: 'json',
                limit: 1,
            },
            headers: {
               
                'User-Agent': 'VRP_Logistics_App/1.0',
            }
        });

        if (response.data && response.data.length > 0) {
            const { lat, lon } = response.data[0];
            return {
                lat: parseFloat(lat),
                lng: parseFloat(lon),
                display_name: response.data[0].display_name
            };
        }
        return null;
    } catch (error) {
        console.error('Geocoding error:', error);
        throw error;
    }
};
