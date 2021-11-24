echo 'environment: test'
export ENV=test

# echo 'Drop tables and seed database'
python test_seed.py
echo 'Data seeded. Begin testing'

python -m unittest