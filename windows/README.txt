
Windows�ł̎g����

- ���s�t�@�C���P�̂œ��삵�܂��B���C�u�����t�@�C���͕s�v�ł��B
- ���s�t�@�C���Ɠ����t�H���_�ɁAcourses-selected.json ���K�v�ł��B
- Windows��ł�-s�I�v�V�����͎g���܂���B�iWindows�p��curses���C�u������
  ���{����T�|�[�g���Ă��Ȃ����߁j

- ���C�Z���X�̊֌W�ŁAffmpeg�͓������Ă��܂���B�C���X�g�[�����Ă��Ȃ��ꍇ
  �͕ʓr�p�ӂ���K�v������܂��B

�yffmpeg�̏����z
 1. ffmpeg���_�E�����[�h�B
    https://www.gyan.dev/ffmpeg/builds/packages/ ��release�̉��ɂ���
    ffmpeg-4.3.2-2021-02-27-full_build.7z �œ���m�F���Ă��܂��B
    ������V�������̂ł���Γ����Ǝv���܂��B
    ��L�̃y�[�W�́Arelease�̉��ɂ���K���Ȃ��̂��_�E�����[�h���܂��B
    essntial_build, full_build�̂ǂ�ł��A7z, zip�̂�����ł������ł��B
    ��������Azip�̒��ň�ԏ�ɂ�����̂�I��ł��������B

 2. �_�E�����[�h�����t�@�C�����𓀁B
    bin�Ƃ����t�H���_�̉���ffmpeg.exe (=ffmpeg)������܂��B
    ���ɂ����낢��ȃt�@�C���������Ă��܂����A�K�v�Ȃ̂�ffmpeg.exe�݂̂�
    ���B

 2. ffmpeg.exe���p�X�̒ʂ����Ƃ���A�������͍�ƃt�H���_ 
    (radio-gogaku-downloader.exe�Ɠ����t�H���_) �ɒu���܂��B


�y�ԑg���X�g�̏����z
 1. courses-all.json���R�s�[���āA�R�s�[�����t�@�C����courses-selected.json
    �Ƃ������O�ɕύX�B
 2. courses-selected.json���������������̓G�f�B�^�ŊJ���A�s�v�Ȕԑg�̓�����
    �s���폜�B�i�s�v�Ȕԑg�̍s�̂ݍ폜���āA����ȊO�͂��̂܂܂ɂ��Ă�����
    �Ɓj
 3. �ҏW���I�������t�@�C����ۑ��B


�y�g�����z
 1. radio-gogaku-downloader.bat�̈�ԉ��̍s�� -d �ȍ~�������ɍ����悤�ɏ���
    ������B
 2. radio-gogaku-downloader.bat�̃A�C�R�����E�N���b�N���ăV���[�g�J�b�g����
    ���B
 3. �V���[�g�J�b�g�̃A�C�R�����E�N���b�N���āA���O���D���Ȃ悤�ɏ���������B
 4. �V���[�g�J�b�g�̃A�C�R�����f�X�N�g�b�v���D���ȏꏊ�ɒu���B
 5. �V���[�g�J�b�g�̃A�C�R�����_�u���N���b�N�Ŏ��s�B
 6. �������s���ɃE�B���h�E���J���̂�����Ȃ�A�V���[�g�J�b�g�̃A�C�R�����E�N
    ���b�N���ăv���p�e�B���J���A�u���s���̑傫���v����u�ŏ����v��I�����āA
    OK�{�^���������B

�y��ȃI�v�V�����z

[-q�I�v�V���� (�����Ƃ̊ԂɃX�y�[�X�����Ă��Ȃ��Ă��悵)]
 -q 0   �� 64kbps MP3�ɕϊ��i�I�v�V���������̏ꍇ�������j
 -q 1   �� 128kbps MP3�ɕϊ�
 -q 2   �� 256kbps MP3�ɕϊ�

[-d �I�v�V�����i�_�E�����[�h��j�̗�]
 -d download    �� radio-gogaku-downloader.exe�̂���t�H���_�̉���download��
                   �����t�H���_�i�����ꍇ�͎����쐬�j�̒��B
 -d C:\Users\XXXX\Music\Gogaku    �� (XXXX�̓��[�U�[��)�u�~���[�W�b�N�v�t�H
                   ���_�̉���Gogaku�Ƃ����t�H���_�i�����ꍇ�͎����쐬�j�̒�
 -d C:/Users/XXXX/Music/Gogaku    �� ��Ɠ����i\�ł�/�ł��悢�j
