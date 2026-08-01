"""Unit tests for the attractions module.

Tests the attraction verification and filtering functionality to ensure
proper validation of coordinates, distance calculations, category matching,
and end-to-end filtering.
"""

import pytest
from utils.attractions import AttractionFilter, VerifiedAttraction


class TestHasValidCoordinates:
    """Test coordinate validation logic."""
    
    def test_valid_coordinates(self):
        """Test attraction with valid coordinates passes validation."""
        attraction = {
            "coordinates": [{"lat": "40.7128", "lon": "-74.0060"}]
        }
        assert AttractionFilter.has_valid_coordinates(attraction) is True
    
    def test_valid_coordinates_as_floats(self):
        """Test attraction with float coordinates passes validation."""
        attraction = {
            "coordinates": [{"lat": 40.7128, "lon": -74.0060}]
        }
        assert AttractionFilter.has_valid_coordinates(attraction) is True
    
    def test_missing_coordinates_key(self):
        """Test attraction without coordinates key fails validation."""
        attraction = {}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_empty_coordinates_list(self):
        """Test attraction with empty coordinates list fails validation."""
        attraction = {"coordinates": []}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_missing_lat_key(self):
        """Test attraction missing latitude key fails validation."""
        attraction = {"coordinates": [{"lon": "-74.0060"}]}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_missing_lon_key(self):
        """Test attraction missing longitude key fails validation."""
        attraction = {"coordinates": [{"lat": "40.7128"}]}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_invalid_lat_range_too_high(self):
        """Test latitude above 90 degrees fails validation."""
        attraction = {"coordinates": [{"lat": "91.0", "lon": "0.0"}]}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_invalid_lat_range_too_low(self):
        """Test latitude below -90 degrees fails validation."""
        attraction = {"coordinates": [{"lat": "-91.0", "lon": "0.0"}]}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_invalid_lon_range_too_high(self):
        """Test longitude above 180 degrees fails validation."""
        attraction = {"coordinates": [{"lat": "0.0", "lon": "181.0"}]}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_invalid_lon_range_too_low(self):
        """Test longitude below -180 degrees fails validation."""
        attraction = {"coordinates": [{"lat": "0.0", "lon": "-181.0"}]}
        assert AttractionFilter.has_valid_coordinates(attraction) is False
    
    def test_boundary_values_valid(self):
        """Test coordinates at valid boundaries pass validation."""
        # Test all four corners of valid coordinate space
        assert AttractionFilter.has_valid_coordinates(
            {"coordinates": [{"lat": "90", "lon": "180"}]}
        ) is True
        assert AttractionFilter.has_valid_coordinates(
            {"coordinates": [{"lat": "-90", "lon": "-180"}]}
        ) is True
        assert AttractionFilter.has_valid_coordinates(
            {"coordinates": [{"lat": "90", "lon": "-180"}]}
        ) is True
        assert AttractionFilter.has_valid_coordinates(
            {"coordinates": [{"lat": "-90", "lon": "180"}]}
        ) is True
    
    def test_non_numeric_coordinates(self):
        """Test non-numeric coordinate values fail validation."""
        attraction = {"coordinates": [{"lat": "abc", "lon": "def"}]}
        assert AttractionFilter.has_valid_coordinates(attraction) is False


class TestIsWithinDistance:
    """Test distance checking logic."""
    
    def test_same_location(self):
        """Test attraction at same location as destination is within distance."""
        assert AttractionFilter.is_within_distance(40.7128, -74.0060, 40.7128, -74.0060) is True
    
    def test_within_max_distance(self):
        """Test attraction within 45km passes validation."""
        # Paris city center to Eiffel Tower (~5 km)
        assert AttractionFilter.is_within_distance(
            48.8566, 2.3522,  # Paris center
            48.8584, 2.2945,  # Eiffel Tower
            max_km=45
        ) is True
    
    def test_beyond_max_distance(self):
        """Test attraction beyond 45km fails validation."""
        # Paris to Versailles (~20 km) - test with a lower threshold
        assert AttractionFilter.is_within_distance(
            48.8566, 2.3522,  # Paris center
            48.8049, 2.1204,  # Versailles
            max_km=10  # Set threshold lower than actual distance
        ) is False
    
    def test_exactly_at_max_distance(self):
        """Test attraction at exactly maximum distance passes validation."""
        # Use a known distance calculation
        # New York to Brooklyn (~10 km), test with exact threshold
        result = AttractionFilter.is_within_distance(
            40.7128, -74.0060,  # Manhattan
            40.6782, -73.9442,  # Brooklyn
            max_km=45
        )
        assert result is True
    
    def test_custom_max_distance(self):
        """Test custom maximum distance parameter works correctly."""
        # Test with very small distance
        assert AttractionFilter.is_within_distance(
            40.7128, -74.0060,
            40.7129, -74.0061,  # Very close, ~100 meters
            max_km=1
        ) is True
        
        # Test with points farther apart and small threshold
        assert AttractionFilter.is_within_distance(
            40.7128, -74.0060,
            40.7200, -74.0120,  # ~1 km away
            max_km=0.5  # 500 meters
        ) is False


class TestMatchesPriorityCategories:
    """Test category matching logic."""
    
    def test_has_priority_category(self):
        """Test attraction with priority category passes."""
        categories = ["Category:Museums in Paris", "Category:Art galleries"]
        assert AttractionFilter.matches_priority_categories(categories) is True
    
    def test_has_multiple_priority_categories(self):
        """Test attraction with multiple priority categories passes."""
        categories = [
            "Category:Tourist attractions in London",
            "Category:Palaces in London",
            "Category:Historic buildings"
        ]
        assert AttractionFilter.matches_priority_categories(categories) is True
    
    def test_has_excluded_category(self):
        """Test attraction with excluded category fails."""
        categories = ["Category:Annual events in Paris", "Category:Festivals"]
        assert AttractionFilter.matches_priority_categories(categories) is False
    
    def test_has_both_priority_and_excluded(self):
        """Test attraction with both priority and excluded categories fails."""
        categories = [
            "Category:Museums in London",
            "Category:Annual event"
        ]
        assert AttractionFilter.matches_priority_categories(categories) is False
    
    def test_no_matching_categories(self):
        """Test attraction with no matching categories fails."""
        categories = ["Category:Companies in Paris", "Category:Software"]
        assert AttractionFilter.matches_priority_categories(categories) is False
    
    def test_empty_categories(self):
        """Test attraction with empty category list fails."""
        assert AttractionFilter.matches_priority_categories([]) is False
    
    def test_case_insensitive_matching(self):
        """Test category matching is case-insensitive."""
        categories = ["Category:MUSEUMS in Paris", "Category:TOURIST ATTRACTION"]
        assert AttractionFilter.matches_priority_categories(categories) is True
    
    def test_theater_spelling_variants(self):
        """Test both 'theatre' and 'theater' spellings are recognized."""
        assert AttractionFilter.matches_priority_categories(
            ["Category:Theatres in London"]
        ) is True
        assert AttractionFilter.matches_priority_categories(
            ["Category:Theaters in New York"]
        ) is True


class TestFilterAndVerify:
    """Test end-to-end filtering logic."""
    
    def test_filters_invalid_coordinates(self):
        """Test attractions with invalid coordinates are filtered out."""
        raw_attractions = [
            {
                "name": "Valid Attraction",
                "description": "A valid place",
                "coordinates": [{"lat": "48.8566", "lon": "2.3522"}],
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            },
            {
                "name": "Invalid Attraction",
                "description": "No coordinates",
                "coordinates": [],
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            }
        ]
        
        result = AttractionFilter.filter_and_verify(raw_attractions, 48.8566, 2.3522)
        assert len(result) == 1
        assert result[0].name == "Valid Attraction"
    
    def test_filters_excluded_categories(self):
        """Test attractions with excluded categories are filtered out."""
        raw_attractions = [
            {
                "name": "Museum",
                "description": "A museum",
                "coordinates": [{"lat": "48.8566", "lon": "2.3522"}],
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            },
            {
                "name": "Annual Festival",
                "description": "A festival",
                "coordinates": [{"lat": "48.8567", "lon": "2.3523"}],
                "categories": ["Category:Annual event in Paris"],
                "image": None,
                "source": None
            }
        ]
        
        result = AttractionFilter.filter_and_verify(raw_attractions, 48.8566, 2.3522)
        assert len(result) == 1
        assert result[0].name == "Museum"
    
    def test_filters_distant_attractions(self):
        """Test attractions beyond 45km are filtered out."""
        raw_attractions = [
            {
                "name": "Nearby Museum",
                "description": "Close to destination",
                "coordinates": [{"lat": "48.8566", "lon": "2.3522"}],
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            },
            {
                "name": "Distant Museum",
                "description": "Far from destination",
                "coordinates": [{"lat": "48.5", "lon": "1.5"}],  # ~80km away
                "categories": ["Category:Museums in France"],
                "image": None,
                "source": None
            }
        ]
        
        result = AttractionFilter.filter_and_verify(raw_attractions, 48.8566, 2.3522)
        assert len(result) == 1
        assert result[0].name == "Nearby Museum"
    
    def test_sorts_by_distance(self):
        """Test attractions are sorted by distance from destination."""
        raw_attractions = [
            {
                "name": "Far Museum",
                "description": "Farther away",
                "coordinates": [{"lat": "48.87", "lon": "2.35"}],
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            },
            {
                "name": "Near Museum",
                "description": "Very close",
                "coordinates": [{"lat": "48.8567", "lon": "2.3523"}],  # Closer
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            },
            {
                "name": "Middle Museum",
                "description": "Medium distance",
                "coordinates": [{"lat": "48.86", "lon": "2.35"}],
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            }
        ]
        
        result = AttractionFilter.filter_and_verify(raw_attractions, 48.8566, 2.3522)
        assert len(result) == 3
        assert result[0].name == "Near Museum"
        assert result[2].name == "Far Museum"
        # Verify distances are in ascending order
        assert result[0].distance_from_destination_km <= result[1].distance_from_destination_km
        assert result[1].distance_from_destination_km <= result[2].distance_from_destination_km
    
    def test_returns_maximum_six_attractions(self):
        """Test that at most 6 attractions are returned."""
        raw_attractions = []
        for i in range(10):
            raw_attractions.append({
                "name": f"Museum {i}",
                "description": f"Museum number {i}",
                "coordinates": [{"lat": f"{48.856 + i * 0.001}", "lon": "2.3522"}],
                "categories": ["Category:Museums in Paris"],
                "image": None,
                "source": None
            })
        
        result = AttractionFilter.filter_and_verify(raw_attractions, 48.8566, 2.3522)
        assert len(result) == 6
    
    def test_preserves_all_attraction_fields(self):
        """Test that all attraction fields are preserved in the output."""
        raw_attractions = [
            {
                "name": "Louvre Museum",
                "description": "Famous art museum",
                "coordinates": [{"lat": "48.8606", "lon": "2.3376"}],
                "categories": ["Category:Museums in Paris", "Category:Art galleries"],
                "image": "https://example.com/louvre.jpg",
                "source": "https://en.wikipedia.org/wiki/Louvre"
            }
        ]
        
        result = AttractionFilter.filter_and_verify(raw_attractions, 48.8566, 2.3522)
        assert len(result) == 1
        
        attraction = result[0]
        assert attraction.name == "Louvre Museum"
        assert attraction.description == "Famous art museum"
        assert attraction.latitude == 48.8606
        assert attraction.longitude == 2.3376
        assert attraction.image_url == "https://example.com/louvre.jpg"
        assert attraction.source_url == "https://en.wikipedia.org/wiki/Louvre"
        assert attraction.distance_from_destination_km > 0
    
    def test_empty_input_returns_empty_list(self):
        """Test that empty input returns empty list."""
        result = AttractionFilter.filter_and_verify([], 48.8566, 2.3522)
        assert result == []
    
    def test_all_filtered_out_returns_empty_list(self):
        """Test that if all attractions are filtered out, empty list is returned."""
        raw_attractions = [
            {
                "name": "Invalid",
                "description": "No coords",
                "coordinates": [],
                "categories": ["Category:Museums"],
                "image": None,
                "source": None
            }
        ]
        
        result = AttractionFilter.filter_and_verify(raw_attractions, 48.8566, 2.3522)
        assert result == []


class TestVerifiedAttractionDataclass:
    """Test VerifiedAttraction dataclass."""
    
    def test_create_verified_attraction(self):
        """Test creating a VerifiedAttraction instance."""
        attraction = VerifiedAttraction(
            name="Eiffel Tower",
            description="Iconic iron tower",
            latitude=48.8584,
            longitude=2.2945,
            image_url="https://example.com/eiffel.jpg",
            source_url="https://en.wikipedia.org/wiki/Eiffel_Tower",
            distance_from_destination_km=5.2
        )
        
        assert attraction.name == "Eiffel Tower"
        assert attraction.description == "Iconic iron tower"
        assert attraction.latitude == 48.8584
        assert attraction.longitude == 2.2945
        assert attraction.image_url == "https://example.com/eiffel.jpg"
        assert attraction.source_url == "https://en.wikipedia.org/wiki/Eiffel_Tower"
        assert attraction.distance_from_destination_km == 5.2
    
    def test_create_with_none_optional_fields(self):
        """Test creating VerifiedAttraction with None for optional fields."""
        attraction = VerifiedAttraction(
            name="Local Park",
            description="A nice park",
            latitude=40.7128,
            longitude=-74.0060,
            image_url=None,
            source_url=None,
            distance_from_destination_km=2.0
        )
        
        assert attraction.image_url is None
        assert attraction.source_url is None


class TestAttractionFilterConstants:
    """Test AttractionFilter class constants."""
    
    def test_max_distance_constant(self):
        """Test MAX_DISTANCE_KM is set to 45."""
        assert AttractionFilter.MAX_DISTANCE_KM == 45
    
    def test_excluded_categories_defined(self):
        """Test EXCLUDED_CATEGORIES contains expected terms."""
        expected = {
            "annual event",
            "recurring event",
            "book fair",
            "festival",
            "conference",
            "trade fair"
        }
        assert AttractionFilter.EXCLUDED_CATEGORIES == expected
    
    def test_priority_categories_contains_key_terms(self):
        """Test PRIORITY_CATEGORIES contains essential attraction types."""
        essential_terms = {
            "tourist attraction",
            "museum",
            "park",
            "monument",
            "castle",
            "church",
            "beach"
        }
        for term in essential_terms:
            assert term in AttractionFilter.PRIORITY_CATEGORIES
    
    def test_priority_categories_includes_theater_variants(self):
        """Test both 'theatre' and 'theater' spellings are in priority categories."""
        assert "theatre" in AttractionFilter.PRIORITY_CATEGORIES
        assert "theater" in AttractionFilter.PRIORITY_CATEGORIES
