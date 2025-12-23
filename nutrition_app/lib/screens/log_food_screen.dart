import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:intl/intl.dart';
import 'package:nutrition_app/main.dart';
import 'package:nutrition_app/models/food.dart';
import 'package:nutrition_app/models/log.dart';
import 'dart:developer' as developer;

class LogFoodScreen extends StatefulWidget {
  final DailyLogModel? editLog;

  const LogFoodScreen({super.key, this.editLog});

  @override
  State<LogFoodScreen> createState() => _LogFoodScreenState();
}

class _LogFoodScreenState extends State<LogFoodScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _image;

  final _foodNameController = TextEditingController();
  final _caloriesController = TextEditingController();
  final _proteinController = TextEditingController();
  final _carbsController = TextEditingController();
  final _fatsController = TextEditingController();
  final _quantityController = TextEditingController();

  final _searchController = TextEditingController();
  List<Food> _searchResults = [];
  bool _isLoading = false;
  bool _isSearching = false;
  Timer? _debounce;

  DateTime _selectedDate = DateTime.now();
  bool _isEditing = false;
  int? _selectedFoodId;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(_onSearchChanged);

    if (widget.editLog != null) {
      _isEditing = true;
      _selectedDate = widget.editLog!.date;
      _quantityController.text = widget.editLog!.quantity.toString();

      if (widget.editLog!.food != null) {
        _foodNameController.text = widget.editLog!.food!.name;
        _caloriesController.text = widget.editLog!.food!.calories.toString();
        _proteinController.text = widget.editLog!.food!.protein.toString();
        _carbsController.text = widget.editLog!.food!.carbs.toString();
        _fatsController.text = widget.editLog!.food!.fats.toString();
      }
    }
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _foodNameController.dispose();
    _caloriesController.dispose();
    _proteinController.dispose();
    _carbsController.dispose();
    _fatsController.dispose();
    _quantityController.dispose();
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      final query = _searchController.text;
      if (query.isNotEmpty) {
        _performSearch(query);
      } else {
        if (mounted) {
          setState(() {
            _searchResults = [];
            _isSearching = false;
          });
        }
      }
    });
  }

  Future<void> _performSearch(String query) async {
    if (!mounted) return;
    setState(() {
      _isSearching = true;
    });

    try {
      final results = await apiService.searchFood(query);
      if (mounted) {
        setState(() {
          _searchResults = results;
        });
      }
    } catch (e) {
      developer.log('Error searching food: $e');
      if (mounted) {
        _showSnackBar('Failed to search food: $e');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSearching = false;
        });
      }
    }
  }

  void _populateFoodFields(Food food) {
    _foodNameController.text = food.name;
    _caloriesController.text = food.calories.toString();
    _proteinController.text = food.protein.toString();
    _carbsController.text = food.carbs.toString();
    _fatsController.text = food.fats.toString();
    _selectedFoodId = food.id;

    if (mounted) {
      setState(() {
        _searchResults = [];
        _searchController.text = '';
        FocusScope.of(context).unfocus();
      });
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? pickedFile = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        setState(() {
          _image = pickedFile;
        });

        // Identify food using AI
        _showSnackBar('Analyzing image with AI...');
        try {
          final result = await apiService.identifyFood(pickedFile.path);
          developer.log('Food identification result: $result');

          // Extract food name from result (backend returns 'food_identified')
          final foodName = result['food_identified'] as String? ?? 
                          result['food_name'] as String? ?? 
                          result['identified_food'] as String?;
          
          if (foodName != null && foodName.isNotEmpty) {
            _showSnackBar('Found: $foodName - Auto-filling...');
            
            // Search for the identified food
            _searchController.text = foodName;
            await _performSearch(foodName);
            
            // AUTO-SELECT: Automatically select the first/best match
            if (_searchResults.isNotEmpty) {
              final bestMatch = _searchResults.first;
              developer.log('Auto-selecting best match: ${bestMatch.name}');
              
              // Auto-populate all nutrition fields
              _populateFoodFields(bestMatch);
              
              _showSnackBar('✅ Auto-filled: ${bestMatch.name}');
            } else {
              _showSnackBar('Found: $foodName (no exact matches, please select manually)');
            }
          } else {
            _showSnackBar('Could not identify food. Please enter manually.');
          }
        } catch (e) {
          developer.log('Food identification error: $e');
          _showSnackBar('AI identification failed. Please search manually.');
        }
      }
    } catch (e) {
      developer.log('Image picker error: $e');
      _showSnackBar('Failed to pick image: $e');
    }
  }

  Future<void> _openFilePicker() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: false,
      );

      if (result != null && result.files.single.path != null) {
        final filePath = result.files.single.path!;
        setState(() {
          _image = XFile(filePath);
        });

        // Identify food using AI
        _showSnackBar('Analyzing image with AI...');
        try {
          final apiResult = await apiService.identifyFood(filePath);
          developer.log('Food identification result: $apiResult');

          // Extract food name from result (backend returns 'food_identified')
          final foodName = apiResult['food_identified'] as String? ?? 
                          apiResult['food_name'] as String? ?? 
                          apiResult['identified_food'] as String?;
          
          if (foodName != null && foodName.isNotEmpty) {
            _showSnackBar('Found: $foodName - Auto-filling...');
            
            // Search for the identified food
            _searchController.text = foodName;
            await _performSearch(foodName);
            
            // AUTO-SELECT: Automatically select the first/best match
            if (_searchResults.isNotEmpty) {
              final bestMatch = _searchResults.first;
              developer.log('Auto-selecting best match: ${bestMatch.name}');
              
              // Auto-populate all nutrition fields
              _populateFoodFields(bestMatch);
              
              _showSnackBar('✅ Auto-filled: ${bestMatch.name}');
            } else {
              _showSnackBar('Found: $foodName (no exact matches, please select manually)');
            }
          } else {
            _showSnackBar('Could not identify food. Please enter manually.');
          }
        } catch (e) {
          developer.log('Food identification error: $e');
          _showSnackBar('AI identification failed. Please search manually.');
        }
      }
    } catch (e) {
      developer.log('File picker error: $e');
      _showSnackBar('Failed to pick file: $e');
    }
  }

  Future<void> _showImageSourceDialog() async {
    await showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Choose Image Source'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: const Text('Camera'),
                onTap: () {
                  Navigator.of(context).pop();
                  _pickImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library),
                title: const Text('Gallery'),
                onTap: () {
                  Navigator.of(context).pop();
                  _pickImage(ImageSource.gallery);
                },
              ),
              ListTile(
                leading: const Icon(Icons.folder_open),
                title: const Text('File Browser'),
                onTap: () {
                  Navigator.of(context).pop();
                  _openFilePicker();
                },
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _logFood() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });

    try {
      int? foodId;
      if (_selectedFoodId != null) {
        foodId = _selectedFoodId;
      } else {
        final newFood = Food(
          name: _foodNameController.text,
          calories: double.tryParse(_caloriesController.text) ?? 0.0,
          protein: double.tryParse(_proteinController.text) ?? 0.0,
          carbs: double.tryParse(_carbsController.text) ?? 0.0,
          fats: double.tryParse(_fatsController.text) ?? 0.0,
        );
        final createdFood = await apiService.createFood(newFood);
        foodId = createdFood.id;
      }

      final quantity = double.tryParse(_quantityController.text) ?? 1.0;
      if (_isEditing && widget.editLog != null) {
        final updateData = {
          'quantity': quantity,
          'food_id': foodId,
          'date': DateFormat('yyyy-MM-dd').format(_selectedDate),
        };
        await apiService.updateLog(widget.editLog!.id, updateData);
      } else {
        final logData = {
          'food_id': foodId,
          'quantity': quantity,
          'date': DateFormat('yyyy-MM-dd').format(_selectedDate),
        };
        await apiService.addLog(logData);
      }

      if (mounted) {
        Navigator.of(context).pop(true);
      }
    } catch (e, s) {
      developer.log('Error logging food: $e');
      developer.log('Stack trace: $s');
      if (mounted) {
        _showSnackBar('Failed to log food: $e');
        Navigator.of(context).pop(false);
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _showSnackBar(String message) {
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Log Food')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  labelText: 'Search Food (e.g., Apple)',
                  border: const OutlineInputBorder(),
                  suffixIcon: _isSearching
                      ? const Padding(
                          padding: EdgeInsets.all(8.0),
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.search),
                ),
              ),
              if (_searchResults.isNotEmpty)
                Container(
                  constraints: const BoxConstraints(maxHeight: 200),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: _searchResults.length,
                    itemBuilder: (context, index) {
                      final food = _searchResults[index];
                      return ListTile(
                        title: Text(food.name),
                        subtitle: Text('Per ${food.servingSize ?? 'N/A'}'),
                        onTap: () => _populateFoodFields(food),
                      );
                    },
                  ),
                ),
              const SizedBox(height: 16),

              // Enhanced AI Food Recognition Section (Fixed Background)
              Container(
                margin: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  // Remove gradient, use solid background to match app theme
                  color: theme.colorScheme.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: theme.colorScheme.outline.withOpacity(0.3),
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: theme.shadowColor.withOpacity(0.08),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header with Icon
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              Icons.smart_toy_rounded,
                              color: theme.colorScheme.onPrimary,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'AI Food Recognition',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.onSurface,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'Smart identification powered by AI',
                                  style: theme.textTheme.bodySmall?.copyWith(
                                    color: theme.colorScheme.onSurfaceVariant,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 20),

                      // Single Feature Chip (Removed unnecessary ones)
                      _buildFeatureChip(
                        theme,
                        Icons.restaurant_rounded,
                        'Nutrition Data',
                      ),

                      const SizedBox(height: 20),

                      // Action Buttons in a Grid (All Green)
                      Row(
                        children: [
                          // Camera Button (Already green)
                          Expanded(
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(
                                  vertical: 16,
                                ),
                                backgroundColor:
                                    theme.colorScheme.primary, // Green
                                foregroundColor: theme.colorScheme.onPrimary,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              onPressed: () => _pickImage(ImageSource.camera),
                              icon: const Icon(Icons.camera_alt),
                              label: const Text('📷 Take Photo'),
                            ),
                          ),

                          const SizedBox(width: 12),

                          // Files Button (Now also green)
                          Expanded(
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(
                                  vertical: 16,
                                ),
                                backgroundColor: theme
                                    .colorScheme
                                    .primary, // Changed to green like camera
                                foregroundColor: theme.colorScheme.onPrimary,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              onPressed: () => _openFilePicker(),
                              icon: const Icon(Icons.folder_open),
                              label: const Text('📁 From Files'),
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 12),

                      // Alternative Dialog Button (Also green)
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            side: BorderSide(
                              color: theme.colorScheme.primary, // Green border
                              width: 1.5,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          onPressed: _showImageSourceDialog,
                          icon: Icon(
                            Icons.image_search_rounded,
                            color: theme.colorScheme.primary, // Green icon
                          ),
                          label: Text(
                            'More Options',
                            style: TextStyle(
                              color: theme.colorScheme.primary, // Green text
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Enhanced Image Preview with Better Feedback
              if (_image != null) ...[
                const SizedBox(height: 16),
                Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: theme.shadowColor.withOpacity(0.15),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: theme.colorScheme.primary.withOpacity(0.3),
                          width: 2,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Image with overlay
                          Stack(
                            children: [
                              Image.file(
                                File(_image!.path),
                                height: 200,
                                width: double.infinity,
                                fit: BoxFit.cover,
                              ),
                              // Success overlay
                              Positioned.fill(
                                child: Container(
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [
                                        Colors.transparent,
                                        Colors.black.withOpacity(0.3),
                                      ],
                                      begin: Alignment.topCenter,
                                      end: Alignment.bottomCenter,
                                    ),
                                  ),
                                ),
                              ),
                              // Success indicator
                              Positioned(
                                top: 12,
                                right: 12,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 4,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.green.shade600,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        Icons.check_circle_rounded,
                                        color: Colors.white,
                                        size: 16,
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        'Analyzed',
                                        style: theme.textTheme.bodySmall
                                            ?.copyWith(
                                              color: Colors.white,
                                              fontWeight: FontWeight.w600,
                                            ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),

                          // Status section with clearer feedback
                          Container(
                            padding: const EdgeInsets.all(16),
                            color: theme.colorScheme.surface,
                            child: Row(
                              children: [
                                Icon(
                                  Icons.restaurant_rounded,
                                  color: theme.colorScheme.primary,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'AI Analysis Complete',
                                        style: theme.textTheme.bodyMedium
                                            ?.copyWith(
                                              color:
                                                  theme.colorScheme.onSurface,
                                              fontWeight: FontWeight.w600,
                                            ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        _selectedFoodId != null
                                            ? 'Nutrition data has been loaded into the form below'
                                            : 'Food identified - select from search results above',
                                        style: theme.textTheme.bodySmall
                                            ?.copyWith(
                                              color: theme
                                                  .colorScheme
                                                  .onSurfaceVariant,
                                            ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],

              const Divider(height: 32),

              Text('Or Log Manually', style: theme.textTheme.headlineSmall),
              const SizedBox(height: 16),

              // Manual logging fields (unchanged)
              TextField(
                controller: _foodNameController,
                decoration: const InputDecoration(
                  labelText: 'Food Name',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _caloriesController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Calories (kcal)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _proteinController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Protein (g)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _carbsController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Carbs (g)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _fatsController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Fats (g)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _quantityController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Quantity (e.g., 1, 100)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24),
              _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      onPressed: _logFood,
                      child: const Text('Log Food'),
                    ),
            ],
          ),
        ),
      ),
    );
  }

  // Helper method for feature chip
  Widget _buildFeatureChip(ThemeData theme, IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.colorScheme.primary.withOpacity(0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: theme.colorScheme.primary),
          const SizedBox(width: 6),
          Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
