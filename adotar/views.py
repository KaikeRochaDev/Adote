from django.shortcuts import render, redirect
from divulgar.models import Pet, Raca
from django.contrib import messages
from django.contrib.messages import constants
from .models import PedidoAdocao
from datetime import datetime
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def listar_pets(request):
    if request.method == 'GET':
        pets = Pet.objects.filter(status='P')
        racas = Raca.objects.all()

        cidade = request.GET.get('cidade')
        raca_filter = request.GET.get('raca')

        if cidade:
            pets = pets.filter(cidade__icontains=cidade)

        if raca_filter:
            pets = pets.filter(raca__id=raca_filter)
            raca_filter = Raca.objects.get(id=raca_filter)
        else:
            raca_filter = request.GET.get('raca')

        return render(request, 'listar_pets.html', {'pets': pets, 'racas': racas, 'cidade': cidade, 'raca_filter':raca_filter})

@login_required
def pedido_adocao(request, id_pet):
    pet = Pet.objects.filter(id=id_pet).filter(status='P')

    if not pet.exists():
        messages.add_message(request, constants.WARNING, 'Esse pet já foi adotado')
        return redirect('/adotar')

    pedido = PedidoAdocao(pet=pet.first(),
                          usuario=request.user,
                          data=datetime.now())

    pedido.save()
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção realizado com sucesso')
    return redirect('/adotar')

@login_required
def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)
    pet = Pet.objects.get(id=pedido.pet.id)

    if status == "A":
        pedido.status = 'AP'
        pet.status = 'A'
        string = '''Olá, sua adoção foi aprovada. ...'''
    elif status == "R":
        string = '''Olá, sua adoção foi recusada. ...'''
        pedido.status = 'R'

    pedido.save()
    if status == "A":
        pet.status = 'A'
        pet.save()

        solicitacoes = PedidoAdocao.objects.filter(pet_id=pet.id).exclude(usuario_id=pedido.usuario.id)
        if solicitacoes:
            for solicitacao in solicitacoes:
                solicitacao.status='R'
                solicitacao.save()
                send_mail(
                    'Sua adoção foi processada',
                    '''Adoção do pet concedida a outro, levando em considereção diversos motivos, 
                    entre eles a data/hora da solicitação.''',
                    request.user.email,
                    [solicitacao.usuario.email,]
                )

    email = send_mail(
        'Sua adoção foi processada',
        string,
        'kaike@gmail.com',
        [pedido.usuario.email,]
    )

    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção processado com sucesso.')

    return redirect('/divulgar/ver_pedido_adocao')